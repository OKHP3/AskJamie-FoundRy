"""SQLite persistence for projects, revision snapshots, and evaluations."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .model import InputError, enforce_protection, normalize_draft


class MissingProject(KeyError):
    pass


class StaleRevision(RuntimeError):
    pass


class InvalidBackup(InputError):
    pass


BACKUP_SCHEMA_VERSION = "1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        if self.data_dir.is_symlink():
            raise ValueError("The private data directory must not be a symbolic link")
        self.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name == "posix":
            self.data_dir.chmod(0o700)
        self.db_path = self.data_dir / "workbench.sqlite3"
        # Secure the file before SQLite writes any private project content.
        for suffix in ("", "-journal", "-wal", "-shm"):
            state_path = Path(str(self.db_path) + suffix)
            if state_path.is_symlink():
                raise ValueError("Private state files must not be symbolic links")
            if state_path.exists() and os.name == "posix":
                state_path.chmod(0o600)
        descriptor = os.open(self.db_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            if os.name == "posix":
                os.fchmod(descriptor, 0o600)
        finally:
            os.close(descriptor)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    draft_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS project_history (
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    draft_json TEXT NOT NULL,
                    PRIMARY KEY (project_id, revision)
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    record_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_evaluations_project ON evaluations(project_id, id);
                """
            )

    @staticmethod
    def _project(row: sqlite3.Row) -> dict[str, Any]:
        draft = json.loads(row["draft_json"])
        return {
            **draft,
            "id": row["id"],
            "revision": row["revision"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "visibility": "private",
            "public_graduation_allowed": False,
        }

    def create(self, draft: dict[str, Any]) -> dict[str, Any]:
        project_id = str(uuid.uuid4())
        now = utc_now()
        encoded = json.dumps(draft, ensure_ascii=False, separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO projects(id, revision, created_at, updated_at, draft_json) VALUES(?, 1, ?, ?, ?)",
                (project_id, now, now, encoded),
            )
            connection.execute(
                "INSERT INTO project_history(project_id, revision, updated_at, draft_json) VALUES(?, 1, ?, ?)",
                (project_id, now, encoded),
            )
        return self.get(project_id)

    def get(self, project_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise MissingProject(project_id)
        return self._project(row)

    def list(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM projects ORDER BY updated_at DESC, id").fetchall()
        return [self._project(row) for row in rows]

    def update(self, project_id: str, revision: int, draft: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if row is None:
                raise MissingProject(project_id)
            if row["revision"] != revision:
                raise StaleRevision(f"stale revision: expected {row['revision']}, received {revision}")
            previous = json.loads(row["draft_json"])
            enforce_protection(previous, draft)
            next_revision = revision + 1
            now = utc_now()
            encoded = json.dumps(draft, ensure_ascii=False, separators=(",", ":"))
            connection.execute(
                "UPDATE projects SET revision = ?, updated_at = ?, draft_json = ? WHERE id = ?",
                (next_revision, now, encoded, project_id),
            )
            connection.execute(
                "INSERT INTO project_history(project_id, revision, updated_at, draft_json) VALUES(?, ?, ?, ?)",
                (project_id, next_revision, now, encoded),
            )
        return self.get(project_id)

    def duplicate(self, project_id: str) -> dict[str, Any]:
        """Create a new revision-one project from the current saved draft."""
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if row is None:
                raise MissingProject(project_id)
            draft = deepcopy(json.loads(row["draft_json"]))
            if draft.get("title"):
                original = draft["title"]
                draft["title"] = f"{original[:3995]} copy"
                if draft["title"] == original:
                    draft["title"] = f"{original[:3993]} copy 2"
            if draft.get("slug"):
                original = draft["slug"]
                draft["slug"] = f"{original[:3995]}-copy"
                if draft["slug"] == original:
                    draft["slug"] = f"{original[:3993]}-copy-2"
            project_id = str(uuid.uuid4())
            now = utc_now()
            encoded = json.dumps(draft, ensure_ascii=False, separators=(",", ":"))
            connection.execute(
                "INSERT INTO projects(id, revision, created_at, updated_at, draft_json) VALUES(?, 1, ?, ?, ?)",
                (project_id, now, now, encoded),
            )
            connection.execute(
                "INSERT INTO project_history(project_id, revision, updated_at, draft_json) VALUES(?, 1, ?, ?)",
                (project_id, now, encoded),
            )
        return self.get(project_id)

    def delete(self, project_id: str) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            result = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            if result.rowcount != 1:
                raise MissingProject(project_id)

    def backup(self) -> dict[str, Any]:
        """Return a versioned, self-contained backup without SQLite internals."""
        with self._connect() as connection:
            project_rows = connection.execute("SELECT * FROM projects ORDER BY id").fetchall()
            history_rows = connection.execute(
                "SELECT * FROM project_history ORDER BY project_id, revision"
            ).fetchall()
            evaluation_rows = connection.execute(
                "SELECT project_id, revision, evaluated_at, record_json FROM evaluations "
                "ORDER BY project_id, id"
            ).fetchall()
        backup = {
            "format": "askjamie-workbench-backup",
            "schema_version": BACKUP_SCHEMA_VERSION,
            "created_at": utc_now(),
            "projects": [
                {
                    "id": row["id"],
                    "revision": row["revision"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "draft": json.loads(row["draft_json"]),
                }
                for row in project_rows
            ],
            "history": [
                {
                    "project_id": row["project_id"],
                    "revision": row["revision"],
                    "updated_at": row["updated_at"],
                    "draft": json.loads(row["draft_json"]),
                }
                for row in history_rows
            ],
            "evaluations": [
                {
                    "project_id": row["project_id"],
                    "revision": row["revision"],
                    "evaluated_at": row["evaluated_at"],
                    "record": json.loads(row["record_json"]),
                }
                for row in evaluation_rows
            ],
        }
        # Do not offer a download that the import contract cannot restore.
        return self._validate_backup(backup)

    @staticmethod
    def _validate_backup(backup: Any) -> dict[str, Any]:
        if not isinstance(backup, dict):
            raise InvalidBackup("backup must be an object")
        expected = {"format", "schema_version", "created_at", "projects", "history", "evaluations"}
        if set(backup) != expected:
            raise InvalidBackup("backup has an unsupported shape")
        if backup["format"] != "askjamie-workbench-backup":
            raise InvalidBackup("backup format is not recognized")
        if backup["schema_version"] != BACKUP_SCHEMA_VERSION:
            raise InvalidBackup(f"backup schema_version must be {BACKUP_SCHEMA_VERSION}")
        if not isinstance(backup["created_at"], str) or not backup["created_at"]:
            raise InvalidBackup("backup.created_at must be a nonempty string")
        for field in ("projects", "history", "evaluations"):
            if not isinstance(backup[field], list) or len(backup[field]) > 1000:
                raise InvalidBackup(f"backup.{field} must be an array of at most 1000 items")

        project_ids: set[str] = set()
        projects: list[dict[str, Any]] = []
        for index, item in enumerate(backup["projects"]):
            if not isinstance(item, dict) or set(item) != {
                "id", "revision", "created_at", "updated_at", "draft"
            }:
                raise InvalidBackup(f"backup.projects[{index}] has an invalid shape")
            project_id = item["id"]
            try:
                uuid.UUID(project_id)
            except (ValueError, AttributeError, TypeError) as error:
                raise InvalidBackup(f"backup.projects[{index}].id is invalid") from error
            if project_id in project_ids:
                raise InvalidBackup(f"backup.projects[{index}].id is duplicated")
            project_ids.add(project_id)
            if (
                isinstance(item["revision"], bool)
                or not isinstance(item["revision"], int)
                or item["revision"] < 1
            ):
                raise InvalidBackup(f"backup.projects[{index}].revision is invalid")
            for field in ("created_at", "updated_at"):
                if not isinstance(item[field], str) or not item[field]:
                    raise InvalidBackup(f"backup.projects[{index}].{field} is invalid")
            try:
                draft, _ = normalize_draft(item["draft"])
            except InputError as error:
                raise InvalidBackup(f"backup.projects[{index}].draft is invalid: {error}") from error
            projects.append({**item, "draft": draft})

        history_keys: set[tuple[str, int]] = set()
        history: list[dict[str, Any]] = []
        for index, item in enumerate(backup["history"]):
            if not isinstance(item, dict) or set(item) != {
                "project_id", "revision", "updated_at", "draft"
            }:
                raise InvalidBackup(f"backup.history[{index}] has an invalid shape")
            key = (item["project_id"], item["revision"])
            if item["project_id"] not in project_ids:
                raise InvalidBackup(f"backup.history[{index}] references an unknown project")
            if (
                isinstance(item["revision"], bool)
                or not isinstance(item["revision"], int)
                or item["revision"] < 1
                or key in history_keys
            ):
                raise InvalidBackup(f"backup.history[{index}].revision is invalid or duplicated")
            if not isinstance(item["updated_at"], str) or not item["updated_at"]:
                raise InvalidBackup(f"backup.history[{index}].updated_at is invalid")
            try:
                draft, _ = normalize_draft(item["draft"])
            except InputError as error:
                raise InvalidBackup(f"backup.history[{index}].draft is invalid: {error}") from error
            history_keys.add(key)
            history.append({**item, "draft": draft})

        evaluations: list[dict[str, Any]] = []
        for index, item in enumerate(backup["evaluations"]):
            if not isinstance(item, dict) or set(item) != {
                "project_id", "revision", "evaluated_at", "record"
            }:
                raise InvalidBackup(f"backup.evaluations[{index}] has an invalid shape")
            if item["project_id"] not in project_ids:
                raise InvalidBackup(f"backup.evaluations[{index}] references an unknown project")
            if (
                isinstance(item["revision"], bool)
                or not isinstance(item["revision"], int)
                or item["revision"] < 1
                or not isinstance(item["evaluated_at"], str)
                or not item["evaluated_at"]
                or not isinstance(item["record"], dict)
            ):
                raise InvalidBackup(f"backup.evaluations[{index}] is invalid")
            if (item["project_id"], item["revision"]) not in history_keys:
                raise InvalidBackup(f"backup.evaluations[{index}] references an unknown history revision")
            evaluations.append(item)

        project_by_id = {item["id"]: item for item in projects}
        for item in projects:
            latest = (item["id"], item["revision"])
            if latest not in history_keys:
                raise InvalidBackup(f"backup is missing the current history for project {item['id']}")
            revisions = sorted(revision for project_id, revision in history_keys if project_id == item["id"])
            if len(revisions) != item["revision"] or any(
                revision != index for index, revision in enumerate(revisions, 1)
            ):
                raise InvalidBackup(f"backup has incomplete history for project {item['id']}")
        for project_id, revision in history_keys:
            if revision > project_by_id[project_id]["revision"]:
                raise InvalidBackup(f"backup history exceeds current revision for {project_id}")
        return {
            **backup,
            "projects": projects,
            "history": history,
            "evaluations": evaluations,
        }

    def import_backup(self, backup: Any) -> int:
        """Atomically replace all local state after complete validation."""
        checked = self._validate_backup(backup)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM projects")
            for item in checked["projects"]:
                connection.execute(
                    "INSERT INTO projects(id, revision, created_at, updated_at, draft_json) VALUES(?, ?, ?, ?, ?)",
                    (
                        item["id"],
                        item["revision"],
                        item["created_at"],
                        item["updated_at"],
                        json.dumps(item["draft"], ensure_ascii=False, separators=(",", ":")),
                    ),
                )
            for item in checked["history"]:
                connection.execute(
                    "INSERT INTO project_history(project_id, revision, updated_at, draft_json) VALUES(?, ?, ?, ?)",
                    (
                        item["project_id"],
                        item["revision"],
                        item["updated_at"],
                        json.dumps(item["draft"], ensure_ascii=False, separators=(",", ":")),
                    ),
                )
            for item in checked["evaluations"]:
                connection.execute(
                    "INSERT INTO evaluations(project_id, revision, evaluated_at, record_json) VALUES(?, ?, ?, ?)",
                    (
                        item["project_id"],
                        item["revision"],
                        item["evaluated_at"],
                        json.dumps(item["record"], ensure_ascii=False),
                    ),
                )
        return len(checked["projects"])

    def history(self, project_id: str) -> list[dict[str, Any]]:
        self.get(project_id)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT revision, updated_at FROM project_history WHERE project_id = ? ORDER BY revision DESC",
                (project_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_evaluation(self, project_id: str, record: dict[str, Any]) -> None:
        self.get(project_id)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO evaluations(project_id, revision, evaluated_at, record_json) VALUES(?, ?, ?, ?)",
                (project_id, record["revision"], record["evaluated_at"], json.dumps(record, ensure_ascii=False)),
            )

    def evaluations(self, project_id: str) -> list[dict[str, Any]]:
        self.get(project_id)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT record_json FROM evaluations WHERE project_id = ? ORDER BY id DESC", (project_id,)
            ).fetchall()
        return [json.loads(row["record_json"]) for row in rows]
