from __future__ import annotations

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath
from unittest.mock import patch

import jsonschema
import yaml

from workbench.model import normalize_draft
from workbench.service import export_project, validate_project
from workbench.store import Store


ROOT = Path(__file__).resolve().parent.parent
MANIFEST_SCHEMA = yaml.safe_load((ROOT / "schemas/manifest.schema.yaml").read_text(encoding="utf-8"))
REGISTRY_ITEM_SCHEMA = yaml.safe_load((ROOT / "schemas/registry.schema.yaml").read_text(encoding="utf-8"))


def decision_graph(hostile_result: str = "Proceed."):
    return {
        "start": "start",
        "nodes": [
            {"id": "start", "question": "Is the request clear?", "yes": "answer", "no": "clarify"},
            {"id": "answer", "result": hostile_result},
            {"id": "clarify", "result": "Ask for missing context."},
        ],
    }


def draft_for_kind(kind: str, **changes):
    base = {
        "title": "Scope Guide",
        "slug": "scope-guide",
        "code": "aj05",
        "family": "core-capability",
        "kind": kind,
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
        "skill_ids": ["calm"],
        "workflow_steps": [],
        "decision": {},
        "eval_cases": [],
    }
    if kind == "workflow":
        base["workflow_steps"] = ["Review the request.", "Return the next concrete step."]
    if kind == "decision-tool":
        base["decision"] = decision_graph()
        base["eval_cases"] = [{"name": "answer path", "answers": {"start": True}, "expected_result": "Proceed."}]
    base.update(changes)
    return base


class ExportAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))
        self.skills_file = Path(self.temp.name) / "skills.json"
        self.skills_file.write_text(json.dumps({
            "sourceRepository": "OKHP3/skillz",
            "sourceCommit": "abc123",
            "generatedAt": "2026-09-01",
            "retrievedAt": "2026-09-07",
            "skills": [
                {
                    "id": "calm",
                    "name": "Calm",
                    "family": "askjamie",
                    "description": "Calm help",
                    "maturity": "draftable",
                    "evidenceStatus": "structural",
                    "sourceUrl": "https://example.test/calm",
                }
            ],
        }), encoding="utf-8")
        self.skills_patch = patch("workbench.service.SKILLS_PATH", self.skills_file)
        self.skills_patch.start()

    def tearDown(self):
        self.skills_patch.stop()
        self.temp.cleanup()

    def _export(self, kind: str, **changes):
        normalized, _ = normalize_draft(draft_for_kind(kind, **changes))
        project = self.store.create(normalized)
        self.assertTrue(validate_project(project)["valid"])
        filename, payload = export_project(project, self.store)
        return project, filename, payload

    def _assert_safe_archive_paths(self, archive: zipfile.ZipFile):
        for name in archive.namelist():
            path = PurePosixPath(name)
            self.assertFalse(path.is_absolute(), name)
            self.assertNotIn("..", path.parts, name)
            self.assertNotIn("\\", name, name)

    def _validate_export_metadata(self, archive: zipfile.ZipFile):
        manifest = yaml.safe_load(archive.read("manifest.yaml"))
        jsonschema.Draft202012Validator(MANIFEST_SCHEMA).validate(manifest)
        proposal = yaml.safe_load(archive.read("exports/registry-proposal.yaml"))["repository"]
        jsonschema.Draft202012Validator(REGISTRY_ITEM_SCHEMA["properties"]["repositories"]["items"]).validate(proposal)
        self.assertEqual(manifest["visibility_control"]["visibility"], "private")
        self.assertFalse(manifest["visibility_control"]["public_graduation_allowed"])
        self.assertEqual(proposal["visibility"], "private")
        self.assertFalse(proposal["public_graduation_allowed"])
        self.assertEqual(yaml.safe_load(archive.read("exports/registry-proposal.yaml"))["status"], "pending")
        self.assertFalse(yaml.safe_load(archive.read("exports/registry-proposal.yaml"))["applied"])

    def test_exports_for_assistant_workflow_and_decision_validate_and_stay_isolated(self):
        hidden = self.store.create(normalize_draft(draft_for_kind("assistant", source_text="BETA_SECRET"))[0])
        self.assertIsNotNone(hidden["id"])

        cases = [
            ("assistant", {"expected_names": {"README.md", "AGENTS.md", "CHANGELOG.md", "LICENSE.md", "manifest.yaml", "origin/source.md", "skill/instructions.md", "prompts/system.md", "docs/specification.md", "tests/evals.json", "exports/project.json", "exports/registry-proposal.yaml", "research/skills.json", "exports/evaluation-records.json"}}),
            ("workflow", {"expected_names": {"README.md", "AGENTS.md", "CHANGELOG.md", "LICENSE.md", "manifest.yaml", "origin/source.md", "skill/instructions.md", "prompts/system.md", "docs/specification.md", "tests/evals.json", "exports/project.json", "exports/registry-proposal.yaml", "research/skills.json", "exports/evaluation-records.json"}}),
            ("decision-tool", {"expected_names": {"README.md", "AGENTS.md", "CHANGELOG.md", "LICENSE.md", "manifest.yaml", "origin/source.md", "skill/instructions.md", "prompts/system.md", "docs/specification.md", "tests/evals.json", "exports/project.json", "exports/registry-proposal.yaml", "research/skills.json", "exports/evaluation-records.json", "decision.json", "index.html"}}),
        ]

        for kind, expectations in cases:
            with self.subTest(kind=kind):
                _, filename, payload = self._export(kind, source_text=f"{kind.upper()}_ALPHA")
                self.assertTrue(filename.endswith(".zip"))
                with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                    names = set(archive.namelist())
                    self._assert_safe_archive_paths(archive)
                    self._validate_export_metadata(archive)
                    self.assertTrue(expectations["expected_names"] <= names)
                    self.assertFalse(any(b"BETA_SECRET" in archive.read(name) for name in names if not name.endswith("/")))
                    if kind != "decision-tool":
                        self.assertNotIn("decision.json", names)
                        self.assertNotIn("index.html", names)

    def test_decision_runner_escapes_hostile_text_and_keeps_restart_controls(self):
        _, _, payload = self._export(
            "decision-tool",
            decision=decision_graph("</script><img src=x onerror=alert(1)>\u2028line"),
        )
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            page = archive.read("index.html").decode("utf-8")
            self.assertIn("data-answer=\"true\"", page)
            self.assertIn("data-answer=\"false\"", page)
            self.assertIn("Restart", page)
            self.assertIn("textContent", page)
            self.assertNotIn("</script><img src=x onerror=alert(1)>", page)
            self.assertIn("\\u003c/script\\u003e", page)
            self.assertIn("\\u2028", page)


if __name__ == "__main__":
    unittest.main()
