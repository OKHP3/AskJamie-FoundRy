from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests" / "browser"))

from browser_diagnostics import (  # noqa: E402
    MAX_DIAGNOSTIC_ENTRIES,
    MAX_DIAGNOSTIC_VALUE_LENGTH,
    MAX_SUMMARY_ENTRIES,
    MAX_SUMMARY_VALUE_LENGTH,
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
    def setUp(self) -> None:
        self.environment = patch.dict(os.environ)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        os.environ.pop("GITHUB_STEP_SUMMARY", None)

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

    def test_unicode_and_multiline_values_keep_failure_evidence_readable(self) -> None:
        diagnostics = BrowserDiagnostics()
        console_text = (
            "コンソール失敗 🚨\r\nfirst line\nsecond line "
            + ("界" * MAX_SUMMARY_VALUE_LENGTH)
        )
        request_url = (
            "https://例え.test/失敗\r\nunexpected-url-line?"
            + ("値" * MAX_SUMMARY_VALUE_LENGTH)
        )
        request_failure = (
            "接続失敗 🔌\rnetwork reset\nretry refused "
            + ("障" * MAX_SUMMARY_VALUE_LENGTH)
        )
        diagnostics._record_console(
            "作業台\r\nsecondary label",
            FakeConsoleMessage(console_text),
        )
        diagnostics._record_failed_request(
            "workbench",
            FakeRequest(request_url),
            status=None,
            failure=request_failure,
        )

        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory)
            diagnostics.write(artifact_dir)

            validate_jsonl_outputs(artifact_dir, file_prefix="workbench")
            console_records = [
                json.loads(line)
                for line in (artifact_dir / "workbench-console.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            request_records = [
                json.loads(line)
                for line in (artifact_dir / "workbench-failed-requests.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            self.assertEqual(console_records[0]["text"], console_text)
            self.assertEqual(request_records[0]["url"], request_url)
            self.assertEqual(request_records[0]["failure"], request_failure)

            summary_lines = (
                artifact_dir / "workbench-failure-summary.md"
            ).read_text(encoding="utf-8").splitlines()
            console_line = next(
                line for line in summary_lines if line.startswith("- [作業台")
            )
            request_line = next(
                line for line in summary_lines if line.startswith("- https://例え.test")
            )

            self.assertNotIn("\r", console_line)
            self.assertNotIn("\r", request_line)
            self.assertIn("作業台  secondary label", console_line)
            self.assertIn("コンソール失敗 🚨  first line second line", console_line)
            self.assertIn("https://例え.test/失敗  unexpected-url-line?", request_line)
            self.assertIn("接続失敗 🔌 network reset retry refused", request_line)
            self.assertLessEqual(
                len(console_line),
                8 + (3 * MAX_SUMMARY_VALUE_LENGTH),
            )
            self.assertLessEqual(
                len(request_line),
                29 + (2 * MAX_SUMMARY_VALUE_LENGTH),
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

    def test_failure_summary_is_appended_to_github_step_summary(self) -> None:
        diagnostics = BrowserDiagnostics()
        diagnostics._record_console("workbench", FakeConsoleMessage("Console failure"))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            step_summary = root / "github-step-summary.md"
            step_summary.write_text("# Earlier step output\n\n", encoding="utf-8")

            with patch.dict(
                os.environ,
                {"GITHUB_STEP_SUMMARY": str(step_summary)},
            ):
                diagnostics.write(
                    root / "artifacts",
                    check_name="Workbench usability",
                    file_prefix="workbench",
                )

            displayed = step_summary.read_text(encoding="utf-8")
            self.assertTrue(displayed.startswith("# Earlier step output\n\n"))
            self.assertIn("# Browser acceptance failure", displayed)
            self.assertIn("- Check: Workbench usability", displayed)
            self.assertIn("[workbench] error: Console failure", displayed)

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
