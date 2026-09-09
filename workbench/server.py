"""Strict localhost HTTP interface for the AskJamie Found-Ry workbench."""

from __future__ import annotations

import json
import mimetypes
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .model import InputError, normalize_answers, normalize_draft, run_decision, validate_answer_nodes
from .service import evaluate_project, export_project, read_registry, read_skills, validate_project
from .store import MissingProject, StaleRevision, Store


MAX_BODY = 1024 * 1024
PROJECT_ROUTE = re.compile(
    r"^/api/projects/([0-9a-fA-F-]{36})(?:/"
    r"(history|validate|preview|evaluate|evaluations|export|duplicate))?$"
)
STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/app.js": "app.js",
    "/styles.css": "styles.css",
    "/favicon.svg": "favicon.svg",
}


class WorkbenchServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], store: Store, static_dir: Path | None = None):
        self.store = store
        self.static_dir = static_dir or Path(__file__).resolve().parent / "static"
        super().__init__(address, WorkbenchHandler)


class WorkbenchHandler(BaseHTTPRequestHandler):
    server: WorkbenchServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        super().log_message(format, *args)

    def _local_host(self) -> bool:
        host = self.headers.get("Host", "")
        port = self.server.server_address[1]
        return host in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def _base_headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")

    def _bytes(self, status: int, body: bytes, content_type: str, extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self._base_headers(content_type, len(body))
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, value: Any) -> None:
        self._bytes(status, json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), "application/json; charset=utf-8")

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def _check_host(self) -> bool:
        if not self._local_host():
            self._error(HTTPStatus.BAD_REQUEST, "Host must be this local workbench")
            self.close_connection = True
            return False
        return True

    def _read_json(self) -> Any:
        if self.headers.get("Transfer-Encoding") is not None:
            raise InputError("Transfer-Encoding is not accepted")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1:
            raise InputError("exactly one Content-Length header is required")
        raw_length = lengths[0]
        if raw_length is None or not raw_length.isascii() or not raw_length.isdigit():
            raise InputError("Content-Length must be a valid decimal integer")
        length = int(raw_length)
        if length < 1:
            raise InputError("request body is required")
        if length > MAX_BODY:
            raise InputError("request body exceeds 1 MiB")
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise InputError("Content-Type must be application/json")
        if self.headers.get("X-Foundry-Request") != "1":
            raise InputError("X-Foundry-Request: 1 is required")
        host = self.headers.get("Host", "")
        if self.headers.get("Origin") != f"http://{host}":
            raise InputError("Origin must match this local workbench")
        body = self.rfile.read(length)
        if len(body) != length:
            raise InputError("request body ended before Content-Length")
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError as error:
            raise InputError("request body must be UTF-8 JSON") from error
        try:
            def reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
                result: dict[str, Any] = {}
                for key, value in pairs:
                    if key in result:
                        raise InputError(f"duplicate JSON field: {key}")
                    result[key] = value
                return result

            return json.loads(
                text,
                object_pairs_hook=reject_pairs,
                parse_constant=lambda value: (_ for _ in ()).throw(InputError(f"invalid JSON number: {value}")),
            )
        except json.JSONDecodeError as error:
            raise InputError(f"invalid JSON: {error.msg}") from error

    def do_GET(self) -> None:
        if not self._check_host():
            return
        path = urlsplit(self.path).path
        try:
            if path == "/api/health":
                self._json(HTTPStatus.OK, {"status": "ok"})
            elif path == "/api/projects":
                self._json(HTTPStatus.OK, {"projects": self.server.store.list()})
            elif path == "/api/registry":
                self._json(HTTPStatus.OK, read_registry())
            elif path == "/api/skills":
                self._json(HTTPStatus.OK, read_skills())
            elif path == "/api/backup":
                backup = self.server.store.backup()
                body = json.dumps(backup, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                self._bytes(
                    HTTPStatus.OK,
                    body,
                    "application/json; charset=utf-8",
                    {"Content-Disposition": 'attachment; filename="askjamie-workbench-backup-v1.json"'},
                )
            else:
                match = PROJECT_ROUTE.fullmatch(path)
                if match:
                    self._project_get(match.group(1), match.group(2))
                elif path in STATIC_FILES:
                    self._static(path)
                else:
                    self._error(HTTPStatus.NOT_FOUND, "route not found")
        except MissingProject:
            self._error(HTTPStatus.NOT_FOUND, "project not found")
        except InputError as error:
            self._error(HTTPStatus.BAD_REQUEST, str(error))
        except RuntimeError as error:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))

    def _project_get(self, project_id: str, action: str | None) -> None:
        project = self.server.store.get(project_id)
        if action is None:
            self._json(HTTPStatus.OK, project)
        elif action == "history":
            self._json(HTTPStatus.OK, {"history": self.server.store.history(project_id)})
        elif action == "validate":
            self._json(HTTPStatus.OK, validate_project(project))
        elif action == "evaluations":
            self._json(HTTPStatus.OK, {"evaluations": self.server.store.evaluations(project_id)})
        elif action == "export":
            filename, body = export_project(project, self.server.store)
            self._bytes(HTTPStatus.OK, body, "application/zip", {"Content-Disposition": f'attachment; filename="{filename}"'})
        else:
            self._error(HTTPStatus.NOT_FOUND, "route not found")

    def _static(self, path: str) -> None:
        filename = STATIC_FILES[path]
        target = self.server.static_dir / filename
        if not target.is_file():
            self._error(HTTPStatus.NOT_FOUND, "static file not found")
            return
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "image/svg+xml"}:
            content_type += "; charset=utf-8"
        self._bytes(HTTPStatus.OK, target.read_bytes(), content_type)

    def do_POST(self) -> None:
        self._write_request("POST")

    def do_PUT(self) -> None:
        self._write_request("PUT")

    def do_DELETE(self) -> None:
        if urlsplit(self.path).path == "/api/projects":
            self.send_error(HTTPStatus.NOT_IMPLEMENTED)
            return
        self._write_request("DELETE")

    @staticmethod
    def _require_confirmation(body: Any, action: str) -> None:
        if not isinstance(body, dict) or set(body) != {"confirm"} or body["confirm"] is not True:
            raise InputError(f"{action} requires an explicit confirmation")

    def _write_request(self, method: str) -> None:
        if not self._check_host():
            return
        self.close_connection = True
        path = urlsplit(self.path).path
        try:
            body = self._read_json()
            if method == "POST" and path == "/api/projects":
                draft, _ = normalize_draft(body)
                self._json(HTTPStatus.CREATED, self.server.store.create(draft))
                return
            if method == "POST" and path == "/api/import":
                if not isinstance(body, dict) or set(body) != {"backup", "confirm"}:
                    raise InputError("import requires backup and explicit confirmation")
                self._require_confirmation({"confirm": body["confirm"]}, "import")
                count = self.server.store.import_backup(body["backup"])
                self._json(HTTPStatus.OK, {"imported": count, "projects": self.server.store.list()})
                return
            match = PROJECT_ROUTE.fullmatch(path)
            if not match:
                self._error(HTTPStatus.NOT_FOUND, "route not found")
                return
            project_id, action = match.groups()
            if method == "PUT" and action is None:
                draft, revision = normalize_draft(body, allow_revision=True)
                self._json(HTTPStatus.OK, self.server.store.update(project_id, revision, draft))
            elif method == "DELETE" and action is None:
                self._require_confirmation(body, "delete")
                self.server.store.delete(project_id)
                self._json(HTTPStatus.OK, {"deleted": project_id})
            elif method == "POST" and action == "duplicate":
                self._require_confirmation(body, "duplicate")
                self._json(HTTPStatus.CREATED, self.server.store.duplicate(project_id))
            elif method == "POST" and action == "preview":
                project = self.server.store.get(project_id)
                if project["kind"] != "decision-tool":
                    raise InputError("preview is available only for decision-tool projects")
                answers = normalize_answers(body)
                validate_answer_nodes(project["decision"], answers)
                self._json(HTTPStatus.OK, run_decision(project["decision"], answers))
            elif method == "POST" and action == "evaluate":
                if not isinstance(body, dict) or body:
                    raise InputError("evaluation body must be an empty object")
                project = self.server.store.get(project_id)
                self._json(HTTPStatus.OK, evaluate_project(project, self.server.store))
            else:
                self._error(HTTPStatus.NOT_FOUND, "route not found")
        except MissingProject:
            self._error(HTTPStatus.NOT_FOUND, "project not found")
        except StaleRevision as error:
            self._error(HTTPStatus.CONFLICT, str(error))
        except InputError as error:
            self._error(HTTPStatus.BAD_REQUEST, str(error))
        except RuntimeError as error:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, str(error))


def create_server(port: int = 8765, data_dir: Path | str = ".foundry-data", static_dir: Path | None = None) -> WorkbenchServer:
    if isinstance(port, bool) or not isinstance(port, int) or not 0 <= port <= 65535:
        raise ValueError("port must be between 0 and 65535")
    return WorkbenchServer(("127.0.0.1", port), Store(Path(data_dir)), static_dir)
