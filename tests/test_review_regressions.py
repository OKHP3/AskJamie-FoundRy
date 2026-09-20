"""Regressions for recovered drafts, pilot evidence, and export cleanup."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from workbench.model import normalize_draft
from workbench.service import evaluate_project
from workbench.store import Store

ROOT = Path(__file__).resolve().parents[1]

class ReviewRegressions(unittest.TestCase):
    def test_pilots_execute_every_authored_case(self):
        for kind in ("assistant", "decision-tool"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                draft, _ = normalize_draft(json.loads((ROOT / "docs/acceptance/pilots" / f"{kind}.json").read_text()))
                store = Store(Path(directory))
                project = store.create(draft)
                result = evaluate_project(project, store)
                self.assertGreater(result["passed"], 0)
                self.assertEqual(result["passed"], len(draft["eval_cases"]))
                self.assertEqual(result["unrun"], 0)

    @unittest.skipUnless(shutil.which("node"), "Node is required for the JavaScript race regression")
    def test_interleaved_recovery_never_overwrites_another_project(self):
        result = subprocess.run([shutil.which("node"), str(ROOT / "tests/draft-recovery-race.cjs")], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejected_export_cleans_temporary_files(self):
        spec = importlib.util.spec_from_file_location("export_runner", ROOT / "tests/browser/export-runner.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "invalid.zip"
            with zipfile.ZipFile(archive, "w") as export:
                export.writestr("../escape.txt", "invalid")
            temporary = tempfile.TemporaryDirectory()
            location = Path(temporary.name)
            with patch.object(module.tempfile, "TemporaryDirectory", return_value=temporary):
                with self.assertRaises(SystemExit): module._extract_export(archive)
            self.assertFalse(location.exists())
