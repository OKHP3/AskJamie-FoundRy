from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "technology-compatibility.yaml"


class BrowserFailureWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_text = WORKFLOW.read_text(encoding="utf-8")
        cls.workflow = yaml.safe_load(cls.workflow_text)
        cls.steps = cls.workflow["jobs"]["browser-acceptance"]["steps"]

    def step_named(self, name: str) -> dict:
        return next(step for step in self.steps if step.get("name") == name)

    def test_controlled_failure_steps_execute_both_browser_paths(self) -> None:
        export = self.step_named("Run exported decision browser acceptance")
        self.assertIn("BROWSER_CONTROLLED_FAILURE=export", export["run"])
        self.assertIn("tests/browser/export-acceptance.py", export["run"])
        self.assertIn("export-failure-summary.md", export["run"])
        self.assertIn('file_prefix="export"', export["run"])

        workbench = self.step_named("Confirm workbench failures leave diagnostics")
        self.assertEqual(workbench["env"]["BROWSER_CONTROLLED_FAILURE"], "workbench")
        self.assertIn("tests/browser/workbench-usability.py", workbench["run"])
        self.assertIn("workbench-failure-summary.md", workbench["run"])
        self.assertIn('file_prefix="workbench"', workbench["run"])

    def test_diagnostics_upload_is_always_run_after_failure_checks(self) -> None:
        upload_index = next(
            index
            for index, step in enumerate(self.steps)
            if step.get("name") == "Upload browser diagnostics"
        )
        export_index = next(
            index
            for index, step in enumerate(self.steps)
            if step.get("name") == "Run exported decision browser acceptance"
        )
        workbench_index = next(
            index
            for index, step in enumerate(self.steps)
            if step.get("name") == "Confirm workbench failures leave diagnostics"
        )
        upload = self.steps[upload_index]

        self.assertGreater(upload_index, export_index)
        self.assertGreater(upload_index, workbench_index)
        self.assertEqual(upload["if"], "${{ always() }}")
        self.assertEqual(upload["uses"], "actions/upload-artifact@v4")
        self.assertEqual(
            upload["with"]["path"],
            "${{ runner.temp }}/foundry-browser-artifacts",
        )


if __name__ == "__main__":
    unittest.main()