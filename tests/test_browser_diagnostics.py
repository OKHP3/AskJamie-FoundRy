from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests" / "browser"))

from browser_diagnostics import (  # noqa: E402
    MAX_DIAGNOSTIC_ENTRIES,
    MAX_DIAGNOSTIC_VALUE_LENGTH,
    MAX_SUMMARY_ENTRIES,
    BrowserDiagnostics,
    validate_jsonl_outputs,
)


class FakePage:
    def __init__(self) -> None:
        self.handlers = {}

    def on(self, event: str, handler) -> None:
        self.handlers[event] = handler


class FakeConsoleMessage:
    type = "error"

    def __init__(self, text: str) -> None:
        self.text = text


class FakeRequest:
    method = "GET"
    resource_type = "fetch"

    def __init__(self, url: str, failure: str | None = None) -> None:
        self.url = url
        self.failure = failure


class FakeResponse:
    def __init__(self, request: FakeRequest, status: int) -> None:
        self.request = request
        self.status = status


class BrowserDiagnosticsTests(unittest.TestCase):
    def test_attach_captures_console_and_failed_request_events(self) -> None:
        page = FakePage()
        diagnostics = BrowserDiagnostics()
        diagnostics.attach(page, "workbench")

        page.handlers["console"](FakeConsoleMessage("Console failure"))
        failed_request = FakeRequest(
            "https://example.test/api/projects",
            failure="connection reset",
        )
        page.handlers["requestfailed"](failed_request)
        page.handlers["response"](
            FakeResponse(FakeRequest("https://example.test/api/skills"), 503)
        )

        self.assertEqual(
            diagnostics.console_messages,
            [{"page": "workbench", "type": "error", "text": "Console failure"}],
        )
        self.assertEqual(
            diagnostics.failed_requests,
            [
                {
                    "failure": "connection reset",
                    "method": "GET",
                    "page": "workbench",
                    "resource_type": "fetch",
                    "status": None,
                    "url": "https://example.test/api/projects",
                },
                {
                    "failure": "HTTP 503",
                    "method": "GET",
                    "page": "workbench",
                    "resource_type": "fetch",
                    "status": 503,
                    "url": "https://example.test/api/skills",
                },
            ],
        )

    def test_values_are_truncated_before_they_enter_evidence(self) -> None:
        diagnostics = BrowserDiagnostics()
        long_value = "x" * (MAX_DIAGNOSTIC_VALUE_LENGTH + 1)
        diagnostics._record_console("workbench", FakeConsoleMessage(long_value))
        diagnostics._record_failed_request(
            "workbench",
            FakeRequest(long_value, failure=long_value),
            status=None,
            failure=long_value,
        )

        self.assertEqual(
            len(diagnostics.console_messages[0]["text"]),
            MAX_DIAGNOSTIC_VALUE_LENGTH,
        )
        failed_request = diagnostics.failed_requests[0]
        self.assertEqual(len(failed_request["url"]), MAX_DIAGNOSTIC_VALUE_LENGTH)
        self.assertEqual(len(failed_request["failure"]), MAX_DIAGNOSTIC_VALUE_LENGTH)

    def test_entry_limit_keeps_jsonl_readable_and_reports_dropped_entries(self) -> None:
        diagnostics = BrowserDiagnostics()
        for index in range(MAX_DIAGNOSTIC_ENTRIES + 7):
            diagnostics._record_console(
                "workbench",
                FakeConsoleMessage(f"console message {index}"),
            )
            diagnostics._record_failed_request(
                "workbench",
                FakeRequest(f"https://example.test/{index}"),
                status=None,
                failure="network failure",
            )

        with tempfile.TemporaryDirectory() as directory:
            diagnostics.write(Path(directory))
            for filename, expected_dropped in (
                ("workbench-console.jsonl", 7),
                ("workbench-failed-requests.jsonl", 7),
            ):
                lines = (Path(directory) / filename).read_text(encoding="utf-8").splitlines()
                records = [json.loads(line) for line in lines]
                self.assertEqual(len(records), MAX_DIAGNOSTIC_ENTRIES + 1)
                self.assertEqual(records[-1], {"truncated": expected_dropped})
                self.assertTrue(all(isinstance(record, dict) for record in records))

    def test_failure_summary_contains_counts_and_first_evidence(self) -> None:
        diagnostics = BrowserDiagnostics()
        diagnostics._record_console("workbench", FakeConsoleMessage("Console failure"))
        diagnostics._record_failed_request(
            "workbench",
            FakeRequest("https://example.test/api/projects"),
            status=503,
            failure="HTTP 503",
        )

        with tempfile.TemporaryDirectory() as directory:
            diagnostics.write(
                Path(directory),
                check_name="Exported decision",
                file_prefix="export",
            )

            summary = (Path(directory) / "export-failure-summary.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("- Check: Exported decision", summary)
            self.assertIn("- Console events captured: 1 (dropped: 0)", summary)
            self.assertIn("- Failed request events captured: 1 (dropped: 0)", summary)
            self.assertIn("[workbench] error: Console failure", summary)
            self.assertIn(
                "https://example.test/api/projects: status 503 (HTTP 503)",
                summary,
            )

    def test_failure_summary_only_includes_first_entries(self) -> None:
        diagnostics = BrowserDiagnostics()
        for index in range(MAX_SUMMARY_ENTRIES + 1):
            diagnostics._record_console(
                "workbench",
                FakeConsoleMessage(f"console message {index}"),
            )

        with tempfile.TemporaryDirectory() as directory:
            diagnostics.write(Path(directory))
            summary = (Path(directory) / "workbench-failure-summary.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("console message 0", summary)
            self.assertIn("console message 4", summary)
            self.assertNotIn("console message 5", summary)

    def test_empty_failure_artifacts_are_written_as_readable_jsonl(self) -> None:
        diagnostics = BrowserDiagnostics()
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory)
            self.assertEqual(list(artifact_dir.iterdir()), [])

            diagnostics.write(artifact_dir)

            self.assertEqual(
                sorted(path.name for path in artifact_dir.iterdir()),
                [
                    "workbench-console.jsonl",
                    "workbench-failed-requests.jsonl",
                    "workbench-failure-summary.md",
                ],
            )
            for path in artifact_dir.glob("*.jsonl"):
                self.assertEqual(
                    [
                        json.loads(line)
                        for line in path.read_text(encoding="utf-8").splitlines()
                    ],
                    [{"message": "No evidence captured."}],
                )

    def test_export_failure_artifacts_validate_as_two_jsonl_outputs(self) -> None:
        diagnostics = BrowserDiagnostics()
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory)
            diagnostics.write(
                artifact_dir,
                check_name="Exported decision",
                file_prefix="export",
            )

            validate_jsonl_outputs(artifact_dir, file_prefix="export")

            self.assertEqual(
                sorted(path.name for path in artifact_dir.glob("export-*.jsonl")),
                [
                    "export-console.jsonl",
                    "export-failed-requests.jsonl",
                ],
            )

    def test_jsonl_validation_rejects_missing_or_malformed_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory)
            (artifact_dir / "export-console.jsonl").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "Missing browser diagnostics"):
                validate_jsonl_outputs(artifact_dir, file_prefix="export")

            (artifact_dir / "export-failed-requests.jsonl").write_text(
                "{not-json}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(AssertionError, "Invalid JSONL"):
                validate_jsonl_outputs(artifact_dir, file_prefix="export")


if __name__ == "__main__":
    unittest.main()
