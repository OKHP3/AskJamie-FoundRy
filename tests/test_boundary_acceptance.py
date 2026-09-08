from __future__ import annotations

import io
import http.client
import json
import socket
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

import yaml

from workbench.model import InputError, normalize_draft, validate_graph
from workbench.server import MAX_BODY, create_server
from workbench.service import export_project
from workbench.store import Store


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


class BoundaryAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))
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
            base.update({
                "Content-Type": "application/json",
                "X-Foundry-Request": "1",
                "Origin": f"http://127.0.0.1:{self.port}",
            })
        base.update(headers or {})
        connection.request(method, path, encoded, base)
        response = connection.getresponse()
        payload = response.read()
        result = (response.status, dict(response.headers), payload)
        connection.close()
        return result

    def raw_response(self, request: bytes) -> tuple[int, bytes]:
        with socket.create_connection(("127.0.0.1", self.port), timeout=3) as connection:
            connection.sendall(request)
            connection.shutdown(socket.SHUT_WR)
            response = b""
            while True:
                chunk = connection.recv(4096)
                if not chunk:
                    break
                response += chunk
        head, body = response.split(b"\r\n\r\n", 1)
        return int(head.split(b" ", 2)[1]), body

    def test_malformed_json_and_request_size_boundaries(self):
        status, _, payload = self.request("POST", "/api/projects", b"\xff")
        self.assertEqual(status, 400)
        self.assertIn("UTF-8 JSON", json.loads(payload)["error"])

        exact_body = b"{}" + b" " * (MAX_BODY - 2)
        status, _, payload = self.request("POST", "/api/projects", exact_body)
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(payload)["revision"], 1)

        too_large = (
            f"POST /api/projects HTTP/1.1\r\nHost: 127.0.0.1:{self.port}\r\n"
            f"Content-Type: application/json\r\nX-Foundry-Request: 1\r\n"
            f"Origin: http://127.0.0.1:{self.port}\r\nContent-Length: {MAX_BODY + 1}\r\n\r\n"
        ).encode()
        status, payload = self.raw_response(too_large)
        self.assertEqual(status, 400)
        self.assertIn("1 MiB", json.loads(payload)["error"])

    def test_origin_host_write_protections_and_unsupported_methods(self):
        self.assertEqual(self.request("POST", "/api/projects", draft(), {"Origin": "https://evil.test"})[0], 400)
        self.assertEqual(self.request("POST", "/api/projects", draft(), {"X-Foundry-Request": "0"})[0], 400)
        self.assertEqual(self.request("GET", "/api/health", headers={"Host": "evil.test"})[0], 400)
        self.assertEqual(self.request("DELETE", "/api/projects")[0], 501)
        self.assertEqual(self.request("PATCH", "/api/projects", draft())[0], 501)

    def test_graph_edge_cases_and_incomplete_answers(self):
        cyclic = {
            "start": "a",
            "nodes": [
                {"id": "a", "question": "A?", "yes": "b", "no": "done"},
                {"id": "b", "question": "B?", "yes": "a", "no": "done"},
                {"id": "done", "result": "Done"},
                {"id": "unused", "result": "Never"},
            ],
        }
        errors = validate_graph(cyclic)
        self.assertTrue(any("cycle" in error for error in errors))
        self.assertTrue(any("unreachable" in error for error in errors))

        normalized, _ = normalize_draft(draft(kind="decision-tool", decision=decision_graph()))
        project = self.store.create(normalized)
        status, _, payload = self.request("POST", f"/api/projects/{project['id']}/preview", {"answers": {}})
        self.assertEqual(status, 200)
        preview = json.loads(payload)
        self.assertFalse(preview["complete"])
        self.assertEqual(preview["next"]["id"], "start")

    def test_protection_invariants_survive_updates_and_export(self):
        protected, _ = normalize_draft(draft(
            family="client-overlay",
            client_org="acme",
            code="aj03",
            parent_capability="OKHP3/askjamie-aj03-enterprise-sleuth",
            bfs_firewall=True,
        ))
        created = self.store.create(protected)
        updated = self.store.update(created["id"], 1, dict(protected, title="Updated Scope Guide"))
        self.assertEqual(updated["client_org"], "acme")
        self.assertEqual(updated["family"], "client-overlay")
        self.assertEqual(updated["parent_capability"], "OKHP3/askjamie-aj03-enterprise-sleuth")
        self.assertTrue(updated["bfs_firewall"])
        self.assertEqual(updated["visibility_lock"], "permanent-private")
        with self.assertRaisesRegex(InputError, "client_org"):
            self.store.update(created["id"], 2, dict(updated, client_org="other"))

        filename, payload = export_project(updated, self.store)
        self.assertEqual(filename, "acme-askjamie-aj03-scope-guide.zip")
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            proposal = yaml.safe_load(archive.read("exports/registry-proposal.yaml"))["repository"]
            self.assertEqual(proposal["client_org"], "acme")
            self.assertEqual(proposal["parent_capability"], "OKHP3/askjamie-aj03-enterprise-sleuth")
            self.assertEqual(proposal["visibility_lock"], "permanent-private")
            self.assertTrue(proposal["bfs_firewall"])

        variant, _ = normalize_draft(draft(
            slug="research-variant",
            code="aj03",
            family="enterprise-sleuth",
        ))
        variant_project = self.store.create(variant)
        variant_filename, variant_payload = export_project(variant_project, self.store)
        self.assertEqual(variant_filename, "askjamie-aj03-research-variant.zip")
        with zipfile.ZipFile(io.BytesIO(variant_payload)) as archive:
            proposal = yaml.safe_load(archive.read("exports/registry-proposal.yaml"))["repository"]
            self.assertEqual(proposal["code"], "aj03")
            self.assertEqual(proposal["family"], "enterprise-sleuth")
            self.assertEqual(proposal["visibility"], "private")
            self.assertFalse(proposal["public_graduation_allowed"])


if __name__ == "__main__":
    unittest.main()
