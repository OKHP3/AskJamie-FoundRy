from __future__ import annotations

import json
from pathlib import Path


MAX_DIAGNOSTIC_ENTRIES = 200
MAX_DIAGNOSTIC_VALUE_LENGTH = 2000


class BrowserDiagnostics:
    """Keep browser evidence bounded and write it only when a check fails."""

    def __init__(self) -> None:
        self.console_messages: list[dict[str, object]] = []
        self.failed_requests: list[dict[str, object]] = []
        self._console_dropped = 0
        self._failed_request_dropped = 0

    @staticmethod
    def _bounded(value: object) -> str:
        return str(value)[:MAX_DIAGNOSTIC_VALUE_LENGTH]

    def _append(
        self,
        entries: list[dict[str, object]],
        entry: dict[str, object],
        kind: str,
    ) -> None:
        if len(entries) < MAX_DIAGNOSTIC_ENTRIES:
            entries.append(entry)
        elif kind == "console":
            self._console_dropped += 1
        else:
            self._failed_request_dropped += 1

    def attach(self, page, label: str) -> None:
        page.on(
            "console",
            lambda message: self._record_console(label, message),
        )
        page.on(
            "requestfailed",
            lambda request: self._record_failed_request(
                label,
                request,
                status=None,
                failure=request.failure,
            ),
        )
        page.on(
            "response",
            lambda response: self._record_response(label, response),
        )

    def _record_console(self, label: str, message) -> None:
        self._append(
            self.console_messages,
            {
                "page": label,
                "type": self._bounded(message.type),
                "text": self._bounded(message.text),
            },
            "console",
        )

    def _record_failed_request(
        self,
        label: str,
        request,
        *,
        status: int | None,
        failure: object,
    ) -> None:
        self._append(
            self.failed_requests,
            {
                "page": label,
                "method": self._bounded(request.method),
                "url": self._bounded(request.url),
                "resource_type": self._bounded(request.resource_type),
                "status": status,
                "failure": self._bounded(failure or "unknown"),
            },
            "request",
        )

    def _record_response(self, label: str, response) -> None:
        if response.status >= 400:
            request = response.request
            self._record_failed_request(
                label,
                request,
                status=response.status,
                failure=f"HTTP {response.status}",
            )

    @staticmethod
    def _write_jsonl(
        path: Path,
        entries: list[dict[str, object]],
        dropped: int,
    ) -> None:
        lines = [json.dumps(entry, sort_keys=True) for entry in entries]
        if dropped:
            lines.append(json.dumps({"truncated": dropped}, sort_keys=True))
        if not lines:
            lines.append(json.dumps({"message": "No evidence captured."}, sort_keys=True))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write(self, artifact_dir: Path) -> None:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        self._write_jsonl(
            artifact_dir / "workbench-console.jsonl",
            self.console_messages,
            self._console_dropped,
        )
        self._write_jsonl(
            artifact_dir / "workbench-failed-requests.jsonl",
            self.failed_requests,
            self._failed_request_dropped,
        )