from __future__ import annotations

import http.client
import io
import json
import os
import stat
import socket
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import jsonschema
import yaml

from workbench.model import InputError, normalize_draft, validate_graph
from workbench.server import create_server
from workbench.service import export_project, validate_project
from workbench.store import StaleRevision, Store


ROOT = Path(__file__).resolve().parent.parent


def draft(**changes):
    value = {
        "title": "Scope Guide",
        "slug": "scope-guide",
        "code": "aj05",
        "family": "core-capability",
        "kind": "assistant",
        "purpose": "Translate a request into a bounded next step.",
        "audience": "People planning a capability.",
        "source_text": "Owner supplied source.",
        "source_reference": "private-note-17",
        "instructions": "Clarify the request and preserve uncertainty.",
        "output_contract": "Return a bounded recommendation.",
        "constraints": "Never imply publication.",
        "client_org": "",
        "parent_capability": "",
        "bfs_firewall": False,
        "visibility_lock": "",
        "skill_ids": [],
        "workflow_steps": [],
        "decision": {},
        "eval_cases": [],
    }
    value.update(changes)
    return value


def decision_graph():
    return {
        "start": "start",
        "nodes": [
            {"id": "start", "question": "Is it clear?", "yes": "answer", "no": "clarify"},
            {"id": "answer", "result": "Proceed."},
            {"id": "clarify", "result": "Ask."},
        ],
    }


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))

    def tearDown(self):
        self.temp.cleanup()

    def test_crud_restart_revision_history_and_stale_write(self):
        normalized, _ = normalize_draft(draft())
        created = self.store.create(normalized)
        self.assertEqual(created["revision"], 1)
        restarted = Store(Path(self.temp.name))
        self.assertEqual(restarted.get(created["id"])["source_text"], "Owner supplied source.")
        changed = dict(normalized, title="Revised")
        updated = restarted.update(created["id"], 1, changed)
        self.assertEqual(updated["revision"], 2)
        self.assertEqual([item["revision"] for item in restarted.history(created["id"])], [2, 1])
        with self.assertRaises(StaleRevision):
            restarted.update(created["id"], 1, normalized)

    def test_protected_client_transition_cannot_be_reversed(self):
        protected, _ = normalize_draft(draft(
            family="client-overlay", client_org="acme", code="aj03",
            parent_capability="OKHP3/askjamie-aj03-enterprise-sleuth",
        ))
        created = self.store.create(protected)
        self.assertEqual(created["visibility_lock"], "permanent-private")
        with self.assertRaisesRegex(InputError, "client_org"):
            self.store.update(created["id"], 1, dict(protected, client_org="other"))
        with self.assertRaisesRegex(InputError, "client-overlay"):
            self.store.update(created["id"], 1, dict(protected, family="core-capability"))
        with self.assertRaisesRegex(InputError, "parent_capability"):
            self.store.update(created["id"], 1, dict(protected, parent_capability="OKHP3/other"))

    @unittest.skipUnless(os.name == "posix", "POSIX owner-only permissions")
    def test_private_state_permissions_on_creation_and_reopen(self):
        self.assertEqual(stat.S_IMODE(self.store.data_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.store.db_path.stat().st_mode), 0o600)
        normalized, _ = normalize_draft(draft())
        project = self.store.create(normalized)
        self.store.data_dir.chmod(0o755)
        self.store.db_path.chmod(0o644)
        reopened = Store(self.store.data_dir)
        self.assertEqual(stat.S_IMODE(reopened.data_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(reopened.db_path.stat().st_mode), 0o600)
        self.assertEqual(reopened.get(project["id"])["source_text"], normalized["source_text"])

    def test_nonfinite_json_numbers_are_rejected(self):
        for value in (json.loads("1e400"), float("-inf"), float("nan")):
            with self.subTest(value=value), self.assertRaisesRegex(InputError, "finite"):
                normalize_draft(draft(decision={"nested": [value]}))

    def test_hostile_and_unknown_input_is_rejected(self):
        with self.assertRaisesRegex(InputError, "unknown field"):
            normalize_draft({**draft(), "visibility": "public"})
        with self.assertRaisesRegex(InputError, "null"):
            normalize_draft(draft(instructions="bad\x00input"))
        with self.assertRaisesRegex(InputError, "client_org requires"):
            normalize_draft(draft(client_org="secret-client"))
        with self.assertRaisesRegex(InputError, "single interior hyphens"):
            normalize_draft(draft(slug="../escape"))


class GraphAndEvaluationTests(unittest.TestCase):
    def test_graph_errors_cover_cycles_dangling_and_unreachable(self):
        cyclic = {"start": "a", "nodes": [
            {"id": "a", "question": "A?", "yes": "a", "no": "done"},
            {"id": "done", "result": "Done"},
            {"id": "unused", "result": "Never"},
        ]}
        errors = validate_graph(cyclic)
        self.assertTrue(any("cycle" in error for error in errors))
        self.assertTrue(any("unreachable" in error for error in errors))
        dangling = {"start": "a", "nodes": [{"id": "a", "question": "A?", "yes": "missing", "no": "missing"}]}
        self.assertTrue(any("dangling" in error for error in validate_graph(dangling)))

    def test_decision_and_supplied_response_evaluations_are_honest(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory))
            decision, _ = normalize_draft(draft(
                kind="decision-tool", decision=decision_graph(),
                eval_cases=[
                    {"name": "yes", "answers": {"start": True}, "expected_result": "Proceed."},
                    {"name": "missing", "answers": {}, "expected_result": "Ask."},
                    {"name": "invalid-extra", "answers": {"start": True, "answer": False}, "expected_result": "Proceed."},
                ],
            ))
            project = store.create(decision)
            from workbench.service import evaluate_project
            record = evaluate_project(project, store)
            self.assertEqual((record["passed"], record["unrun"]), (1, 2))
            self.assertIn("non-question", record["cases"][2]["detail"])

            assistant, _ = normalize_draft(draft(eval_cases=[
                {"name": "blank", "input": "x", "response": "", "required": [], "forbidden": []},
                {"name": "literal", "input": "x", "response": "Hello World", "required": ["World"], "forbidden": ["world"]},
            ]))
            assistant_project = store.create(assistant)
            record = evaluate_project(assistant_project, store)
            self.assertEqual((record["passed"], record["unrun"]), (1, 1))
            self.assertIn("no AI", record["cases"][1]["detail"])


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))
        self.skills_file = Path(self.temp.name) / "skills.json"
        self.skills_file.write_text(json.dumps({
            "sourceRepository": "OKHP3/skillz", "sourceCommit": "abc123",
            "generatedAt": "2026-09-01", "retrievedAt": "2026-09-07",
            "skills": [{"id": "calm", "name": "Calm", "family": "askjamie", "description": "Calm help",
                        "maturity": "draftable", "evidenceStatus": "structural", "sourceUrl": "https://example.test/calm"}],
        }), encoding="utf-8")
        self.skills_patch = patch("workbench.service.SKILLS_PATH", self.skills_file)
        self.skills_patch.start()

    def tearDown(self):
        self.skills_patch.stop()
        self.temp.cleanup()

    def test_incomplete_draft_saves_but_export_is_blocked(self):
        incomplete, _ = normalize_draft({})
        project = self.store.create(incomplete)
        result = validate_project(project)
        self.assertFalse(result["valid"])
        self.assertTrue(any("title" in error for error in result["errors"]))
        with self.assertRaisesRegex(InputError, "Export blocked"):
            export_project(project, self.store)

    def test_generated_manifest_zip_layout_placeholders_and_isolation(self):
        first, _ = normalize_draft(draft(skill_ids=["calm"], source_text="ALPHA_ONLY"))
        second, _ = normalize_draft(draft(slug="other", code="aj06", source_text="BETA_SECRET"))
        project = self.store.create(first)
        self.store.create(second)
        filename, payload = export_project(project, self.store)
        self.assertEqual(filename, "askjamie-aj05-scope-guide.zip")
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = set(archive.namelist())
            self.assertFalse(any(b"BETA_SECRET" in archive.read(name) for name in names if not name.endswith("/")))
            required = {
                "README.md", "AGENTS.md", "CHANGELOG.md", "LICENSE.md", "manifest.yaml",
                "origin/source.md", "skill/instructions.md", "prompts/system.md", "docs/specification.md",
                "tests/evals.json", "exports/project.json", "exports/registry-proposal.yaml",
                "research/skills.json", "exports/evaluation-records.json",
            }
            self.assertTrue(required <= names)
            self.assertNotIn("ABOUT.md", names)
            manifest = yaml.safe_load(archive.read("manifest.yaml"))
            schema = yaml.safe_load((ROOT / "schemas/manifest.schema.yaml").read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(manifest)
            self.assertEqual(manifest["visibility_control"], {"visibility": "private", "public_graduation_allowed": False})
            for name in ("README.md", "AGENTS.md", "CHANGELOG.md", "manifest.yaml"):
                text = archive.read(name).decode("utf-8")
                self.assertNotIn("Template instruction", text)
                self.assertNotIn("YYYY-MM-DD", text)
                self.assertNotIn("[DISPLAY_NAME]", text)
            selected = json.loads(archive.read("research/skills.json"))
            self.assertEqual(selected["sourceCommit"], "abc123")
            self.assertEqual([item["id"] for item in selected["skills"]], ["calm"])

    def test_decision_export_is_offline_and_script_safe(self):
        graph = decision_graph()
        graph["nodes"][1]["result"] = "</script><b>unsafe</b>\u2028next"
        normalized, _ = normalize_draft(draft(kind="decision-tool", decision=graph))
        project = self.store.create(normalized)
        _, payload = export_project(project, self.store)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            page = archive.read("index.html").decode("utf-8")
            self.assertIn("Restart", page)
            self.assertIn("textContent", page)
            self.assertNotIn("</script><b>unsafe", page)
            self.assertIn("\\u003c/script\\u003e", page)
            self.assertIn("\\u2028", page)
            self.assertIn("open `index.html`", archive.read("README.md").decode("utf-8"))

    def test_overlay_parent_and_protection_are_preserved(self):
        normalized, _ = normalize_draft(draft(
            title="Acme Sleuth", slug="sleuth", code="aj03", family="client-overlay", client_org="acme",
            parent_capability="askjamie-aj03-enterprise-sleuth", bfs_firewall=True,
        ))
        project = self.store.create(normalized)
        _, payload = export_project(project, self.store)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            proposal = yaml.safe_load(archive.read("exports/registry-proposal.yaml"))["repository"]
            self.assertEqual(proposal["parent_capability"], "OKHP3/askjamie-aj03-enterprise-sleuth")
            self.assertEqual(proposal["visibility_lock"], "permanent-private")
            self.assertTrue(proposal["bfs_firewall"])


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = create_server(0, Path(self.temp.name))
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        encoded = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        base = {"Host": f"127.0.0.1:{self.port}"}
        if encoded is not None:
            base.update({"Content-Type": "application/json", "X-Foundry-Request": "1", "Origin": f"http://127.0.0.1:{self.port}"})
        base.update(headers or {})
        connection.request(method, path, encoded, base)
        response = connection.getresponse()
        payload = response.read()
        result = (response.status, dict(response.headers), payload)
        connection.close()
        return result

    def raw_status(self, request: bytes) -> int:
        with socket.create_connection(("127.0.0.1", self.port), timeout=3) as connection:
            connection.sendall(request)
            connection.shutdown(socket.SHUT_WR)
            response = b""
            while True:
                chunk = connection.recv(4096)
                if not chunk:
                    break
                response += chunk
        return int(response.split(b" ", 2)[1])

    def test_http_contract_and_stale_revision(self):
        status, headers, payload = self.request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload), {"status": "ok"})
        self.assertEqual(headers["Cache-Control"], "no-store")
        status, _, payload = self.request("POST", "/api/projects", draft())
        self.assertEqual(status, 201)
        project = json.loads(payload)
        update = draft(title="Updated", revision=project["revision"])
        self.assertEqual(self.request("PUT", f"/api/projects/{project['id']}", update)[0], 200)
        self.assertEqual(self.request("PUT", f"/api/projects/{project['id']}", update)[0], 409)

    def test_write_protections_and_static_allowlist(self):
        self.assertEqual(self.request("POST", "/api/projects", draft(), {"Origin": "https://evil.test"})[0], 400)
        self.assertEqual(self.request("POST", "/api/projects", draft(), {"X-Foundry-Request": "0"})[0], 400)
        self.assertEqual(self.request("GET", "/api/health", headers={"Host": "evil.test"})[0], 400)
        self.assertEqual(self.request("GET", "/../registry/index.yaml")[0], 404)

    def test_preview_rejects_terminal_or_unknown_answer_ids(self):
        status, _, payload = self.request("POST", "/api/projects", draft(kind="decision-tool", decision=decision_graph()))
        project = json.loads(payload)
        status, _, payload = self.request("POST", f"/api/projects/{project['id']}/preview", {"answers": {"answer": True}})
        self.assertEqual(status, 400)
        self.assertIn("non-question", json.loads(payload)["error"])

    def test_invalid_framing_json_and_unknown_route(self):
        status, _, _ = self.request("POST", "/api/projects", b"{not-json")
        self.assertEqual(status, 400)
        status, _, _ = self.request("POST", "/api/projects", b'{"title":"a","title":"b"}')
        self.assertEqual(status, 400)
        base = (f"POST /api/projects HTTP/1.1\r\nHost: 127.0.0.1:{self.port}\r\n"
                f"Origin: http://127.0.0.1:{self.port}\r\nContent-Type: application/json\r\n"
                "X-Foundry-Request: 1\r\n")
        self.assertEqual(self.raw_status((base + "\r\n").encode()), 400)
        self.assertEqual(self.raw_status((base + "Transfer-Encoding: chunked\r\n\r\n2\r\n{}\r\n0\r\n\r\n").encode()), 400)
        self.assertEqual(self.raw_status((base + f"Content-Length: {1024 * 1024 + 1}\r\n\r\n").encode()), 400)
        self.assertEqual(self.request("POST", "/api/nope", {})[0], 404)


if __name__ == "__main__":
    unittest.main()
