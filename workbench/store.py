"""SQLite persistence for projects, revision snapshots, and evaluations."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .model import enforce_protection


class MissingProject(KeyError):
    pass


class StaleRevision(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "workbench.sqlite3"
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
