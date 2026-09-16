"""Provider-independent acceptance harness for a future hosted authoring backend."""

from __future__ import annotations

import io
import hashlib
import json
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from workbench.model import normalize_draft
from workbench.service import evaluate_project, export_project
from workbench.store import MissingProject, Store


SAFE_DENIAL = {"status": 404, "error": "object not found"}
UNAUTHENTICATED_DENIAL = {"status": 401, "error": "authentication required"}
OPERATIONS = ("read", "write", "history", "evaluate", "export", "duplicate", "delete")
EXPECTED_PACKAGE_FILES = {
    "AGENTS.md", "CHANGELOG.md", "LICENSE.md", "README.md", "manifest.yaml",
    "docs/specification.md", "exports/evaluation-records.json",
    "exports/project.json", "exports/registry-proposal.yaml", "origin/source.md",
    "prompts/system.md", "research/skills.json", "skill/instructions.md",
    "tests/evals.json",
}
PUBLIC_FORBIDDEN = (
    b"SQLite format 3", b"SESSION_SECRET", b".foundry-data", b"workbench.sqlite",
    b"/api/", b"localStorage", b"sessionStorage", b"fetch(",
    b"SOURCE_ALPHA_", b"SOURCE_BETA_", b"client-alpha-", b"client-beta-",
)


class HostedIsolationBackend(Protocol):
    """Contract a selected hosted provider adapter must satisfy."""

    def invoke(self, principal: str, operation: str, object_id: str) -> dict[str, Any]: ...
    def snapshot(self, principal: str) -> str: ...
    def inspect_package(self, principal: str, object_id: str) -> bytes | dict[str, Any]: ...
    def backup(self, principal: str) -> tuple[str, dict[str, Any]]: ...
    def download_backup(self, principal: str, backup_id: str) -> dict[str, Any]: ...
    def restore(self, principal: str, backup_id: str) -> dict[str, Any]: ...
    def invoke_restored(
        self, principal: str, backup_id: str, operation: str, object_id: str
    ) -> dict[str, Any]: ...
    def snapshot_restored(self, principal: str, backup_id: str) -> str: ...
    def expire(self, principal: str, backup_id: str) -> None: ...
    def retention_status(self, principal: str, backup_id: str) -> dict[str, Any]: ...
    def invoke_with_claimed_workspace(
        self, principal: str, claimed_workspace: str, operation: str, object_id: str
    ) -> dict[str, Any]: ...
    def revoke_session(self, principal: str) -> None: ...
    def restore_session(self, principal: str, workspace_id: str) -> None: ...
    def support_probe(self, support_actor: str, workspace_id: str) -> dict[str, Any]: ...
    def unauthenticated_probe(self, path: str) -> dict[str, Any]: ...
    def route_inventory(self) -> list[dict[str, Any]]: ...
    def logs(self) -> list[dict[str, Any]]: ...
    def cache(self) -> dict[str, Any]: ...


@dataclass
class Evidence:
    checks: list[dict[str, Any]] = field(default_factory=list)

    def record(self, claim: str, passed: bool, detail: str) -> None:
        self.checks.append({"claim": claim, "status": "PASS" if passed else "FAIL", "detail": detail})

    def report(self) -> dict[str, Any]:
        return {
            "format": "askjamie-hosted-isolation-proof",
            "schema_version": 1,
            "status": "PASS" if all(item["status"] == "PASS" for item in self.checks) else "FAIL",
            "checks": self.checks,
        }


class ReferenceWorkspaceBackend:
    """Deterministic local adapter used to validate the provider contract itself."""

    def __init__(self, root: Path):
        self.root = root
        self.stores: dict[str, Store] = {}
        self.sessions: dict[str, str] = {}
        self.revoked_sessions: set[str] = set()
        self.owners: dict[str, str] = {}
        self.backups: dict[str, tuple[str, dict[str, Any] | None, bool]] = {}
        self.restores: dict[str, tuple[str, Store]] = {}
        self.audit: list[dict[str, Any]] = []

    def add_workspace(self, workspace_id: str) -> Store:
        store = Store(self.root / "workspaces" / workspace_id)
        self.stores[workspace_id] = store
        return store

    def add_principal(self, principal: str, workspace_id: str) -> None:
        self.sessions[principal] = workspace_id

    def register(self, workspace_id: str, object_id: str) -> None:
        self.owners[object_id] = workspace_id

    def _owned(self, principal: str, object_id: str) -> tuple[str, Store]:
        if principal in self.revoked_sessions:
            raise MissingProject(object_id)
        workspace_id = self.sessions.get(principal)
        if workspace_id is None:
            raise MissingProject(object_id)
        if self.owners.get(object_id) != workspace_id:
            raise MissingProject(object_id)
        return workspace_id, self.stores[workspace_id]

    def _log(self, workspace_id: str, operation: str, outcome: str) -> None:
        self.audit.append({"workspace": workspace_id, "operation": operation, "outcome": outcome})

    @staticmethod
    def _snapshot_store(store: Store) -> str:
        state = store.backup()
        state.pop("created_at")
        return hashlib.sha256(
            json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def snapshot(self, principal: str) -> str:
        return self._snapshot_store(self.stores[self.sessions[principal]])

    def invoke(self, principal: str, operation: str, object_id: str) -> dict[str, Any]:
        try:
            workspace_id, store = self._owned(principal, object_id)
            project = store.get(object_id)
            if operation == "read":
                result = {"status": 200, "id": project["id"]}
            elif operation == "write":
                updated = store.update(object_id, project["revision"], {
                    key: value for key, value in project.items()
                    if key not in {"id", "revision", "created_at", "updated_at", "visibility", "public_graduation_allowed"}
                })
                result = {"status": 200, "revision": updated["revision"]}
            elif operation == "history":
                result = {"status": 200, "count": len(store.history(object_id))}
            elif operation == "evaluate":
                result = {"status": 200, "passed": evaluate_project(project, store)["passed"]}
            elif operation == "export":
                result = {"status": 200, "bytes": len(export_project(project, store)[1])}
            elif operation == "duplicate":
                duplicate = store.duplicate(object_id)
                self.register(workspace_id, duplicate["id"])
                result = {"status": 201, "id": duplicate["id"]}
            elif operation == "delete":
                store.delete(object_id)
                self.owners.pop(object_id, None)
                result = {"status": 200}
            else:
                raise ValueError(operation)
            self._log(workspace_id, operation, "allowed")
            return result
        except MissingProject:
            self._log(self.sessions.get(principal, "unknown"), operation, "denied")
            return dict(SAFE_DENIAL)

    def inspect_package(self, principal: str, object_id: str) -> bytes | dict[str, Any]:
        try:
            workspace_id, store = self._owned(principal, object_id)
            payload = export_project(store.get(object_id), store)[1]
            self._log(workspace_id, "package", "allowed")
            return payload
        except MissingProject:
            self._log(self.sessions.get(principal, "unknown"), "package", "denied")
            return dict(SAFE_DENIAL)

    def backup(self, principal: str) -> tuple[str, dict[str, Any]]:
        workspace_id = self.sessions[principal]
        backup = self.stores[workspace_id].backup()
        backup_id = f"{workspace_id}-backup-{len(self.backups) + 1}"
        self.backups[backup_id] = (workspace_id, backup, False)
        return backup_id, backup

    def download_backup(self, principal: str, backup_id: str) -> dict[str, Any]:
        workspace_id = self.sessions[principal]
        owner, backup, expired = self.backups.get(backup_id, ("", {}, True))
        if owner != workspace_id or expired or backup is None:
            self._log(workspace_id, "backup-download", "denied")
            return dict(SAFE_DENIAL)
        self._log(workspace_id, "backup-download", "allowed")
        return {"status": 200, "backup": backup}

    def restore(self, principal: str, backup_id: str) -> dict[str, Any]:
        workspace_id = self.sessions[principal]
        owner, backup, expired = self.backups.get(backup_id, ("", {}, True))
        if owner != workspace_id or expired or backup is None:
            self._log(workspace_id, "restore", "denied")
            return dict(SAFE_DENIAL)
        isolated = Store(self.root / "restores" / workspace_id / backup_id)
        isolated.import_backup(backup)
        self.restores[backup_id] = (workspace_id, isolated)
        self._log(workspace_id, "restore", "allowed")
        projects = isolated.list()
        return {
            "status": 200,
            "isolated": True,
            "workspace": workspace_id,
            "location": str(isolated.data_dir.relative_to(self.root)),
            "project_ids": sorted(item["id"] for item in projects),
            "private": all(
                item["visibility"] == "private"
                and item["public_graduation_allowed"] is False
                and item["visibility_lock"] == "permanent-private"
                and item["bfs_firewall"] is True
                for item in projects
            ),
        }

    def invoke_restored(
        self, principal: str, backup_id: str, operation: str, object_id: str
    ) -> dict[str, Any]:
        workspace_id = self.sessions[principal]
        owner, store = self.restores.get(backup_id, ("", None))
        if owner != workspace_id or store is None:
            self._log(workspace_id, f"restored-{operation}", "denied")
            return dict(SAFE_DENIAL)
        try:
            project = store.get(object_id)
        except MissingProject:
            self._log(workspace_id, f"restored-{operation}", "denied")
            return dict(SAFE_DENIAL)
        if operation == "read":
            result = {"status": 200, "id": project["id"]}
        elif operation == "write":
            updated = store.update(object_id, project["revision"], {
                key: value for key, value in project.items()
                if key not in {"id", "revision", "created_at", "updated_at", "visibility", "public_graduation_allowed"}
            })
            result = {"status": 200, "revision": updated["revision"]}
        elif operation == "history":
            result = {"status": 200, "count": len(store.history(object_id))}
        elif operation == "evaluate":
            result = {"status": 200, "passed": evaluate_project(project, store)["passed"]}
        elif operation == "export":
            result = {"status": 200, "bytes": len(export_project(project, store)[1])}
        elif operation == "duplicate":
            result = {"status": 201, "id": store.duplicate(object_id)["id"]}
        elif operation == "delete":
            store.delete(object_id)
            result = {"status": 200}
        else:
            raise ValueError(operation)
        self._log(workspace_id, f"restored-{operation}", "allowed")
        return result

    def snapshot_restored(self, principal: str, backup_id: str) -> str:
        workspace_id = self.sessions[principal]
        owner, store = self.restores.get(backup_id, ("", None))
        if owner != workspace_id or store is None:
            return "unavailable"
        return self._snapshot_store(store)

    def expire(self, principal: str, backup_id: str) -> None:
        workspace_id = self.sessions[principal]
        owner, backup, _ = self.backups[backup_id]
        if owner != workspace_id:
            raise MissingProject(backup_id)
        self.backups[backup_id] = (owner, None, True)

    def retention_status(self, principal: str, backup_id: str) -> dict[str, Any]:
        workspace_id = self.sessions[principal]
        owner, backup, expired = self.backups.get(backup_id, ("", None, True))
        if owner != workspace_id:
            return dict(SAFE_DENIAL)
        return {
            "status": "deleted" if expired and backup is None else "retained",
            "payload_present": backup is not None,
        }

    def invoke_with_claimed_workspace(
        self, principal: str, claimed_workspace: str, operation: str, object_id: str
    ) -> dict[str, Any]:
        actual_workspace = self.sessions.get(principal)
        if actual_workspace is None or claimed_workspace != actual_workspace:
            self._log(actual_workspace or "unknown", operation, "denied")
            return dict(SAFE_DENIAL)
        return self.invoke(principal, operation, object_id)

    def revoke_session(self, principal: str) -> None:
        self.revoked_sessions.add(principal)

    def restore_session(self, principal: str, workspace_id: str) -> None:
        self.sessions[principal] = workspace_id
        self.revoked_sessions.discard(principal)

    def support_probe(self, support_actor: str, workspace_id: str) -> dict[str, Any]:
        self._log(workspace_id, "support-access", "denied")
        return dict(SAFE_DENIAL)

    def unauthenticated_probe(self, path: str) -> dict[str, Any]:
        self._log("unauthenticated", "route-probe", "denied")
        return dict(UNAUTHENTICATED_DENIAL)

    def route_inventory(self) -> list[dict[str, Any]]:
        return [
            {"route": "/api/projects", "auth_required": True, "public": False},
            {"route": "/api/projects/{id}", "auth_required": True, "public": False},
            {"route": "/api/projects/{id}/export", "auth_required": True, "public": False},
            {"route": "/api/backup", "auth_required": True, "public": False},
            {"route": "/api/import", "auth_required": True, "public": False},
        ]

    def logs(self) -> list[dict[str, Any]]:
        return list(self.audit)

    def cache(self) -> dict[str, Any]:
        return {"entries": 0, "private_payloads": []}


def synthetic_draft(label: str, object_label: str = "project") -> dict[str, Any]:
    marker = f"{label}_{object_label.upper().replace('-', '_')}_PRIVATE"
    draft, _ = normalize_draft({
        "title": f"{label} {object_label} Guide",
        "slug": f"{label.lower()}-{object_label}-guide", "code": "aj03",
        "family": "client-overlay", "kind": "assistant",
        "purpose": f"Purpose {marker}", "audience": "Synthetic reviewers",
        "source_text": f"SOURCE_{marker}", "source_reference": f"REF_{marker}",
        "instructions": "Keep private.", "output_contract": "Return evidence.",
        "constraints": "No publication.",
        "client_org": f"client-{label.lower()}-{object_label}-private",
        "parent_capability": "OKHP3/askjamie-aj03-enterprise-sleuth",
        "bfs_firewall": True, "visibility_lock": "", "skill_ids": [],
        "workflow_steps": [], "decision": {}, "eval_cases": [{
            "name": "synthetic", "input": "check", "response": "evidence",
            "required": ["evidence"], "forbidden": ["publish"],
        }],
    })
    return draft


def run_isolation_proof(
    backend: HostedIsolationBackend,
    ids: dict[str, dict[str, str]],
    principals: dict[str, str],
) -> dict[str, Any]:
    evidence = Evidence()

    selected_id = ids["alpha"]["package"]
    package = backend.inspect_package(principals["alpha"], selected_id)
    if not isinstance(package, bytes):
        evidence.record("package-containment", False, "Owned package request was denied.")
        return evidence.report()
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        file_names = {name for name in archive.namelist() if not name.endswith("/")}
        package_bytes = b"\n".join(archive.read(name) for name in file_names)
        project = json.loads(archive.read("exports/project.json"))
        manifest = archive.read("manifest.yaml")
        proposal = archive.read("exports/registry-proposal.yaml")
    excluded_ids = [
        object_id for workspace_ids in ids.values() for object_id in workspace_ids.values()
        if object_id != selected_id
    ]
    excluded_canaries: list[bytes] = []
    for workspace, workspace_ids in ids.items():
        for object_label, object_id in workspace_ids.items():
            if object_id == selected_id:
                continue
            marker = f"{workspace.upper()}_{object_label.upper().replace('-', '_')}_PRIVATE"
            excluded_canaries.extend((
                f"SOURCE_{marker}".encode(),
                f"REF_{marker}".encode(),
                f"client-{workspace}-{object_label}-private".encode(),
            ))
    evidence.record(
        "package-containment",
        file_names == EXPECTED_PACKAGE_FILES
        and project["id"] == selected_id
        and project["visibility"] == "private"
        and project["public_graduation_allowed"] is False
        and project["visibility_lock"] == "permanent-private"
        and project["bfs_firewall"] is True
        and not any(object_id.encode() in package_bytes for object_id in excluded_ids)
        and not any(canary in package_bytes for canary in excluded_canaries)
        and b"SQLite format 3" not in package_bytes
        and b"SESSION_SECRET" not in package_bytes
        and b"permanent-private" in manifest
        and b"permanent-private" in proposal,
        "Package inventory contains exactly the selected project identity and preserved privacy controls.",
    )
    evidence.record(
        "own-package-beta",
        isinstance(backend.inspect_package(principals["beta"], ids["beta"]["package"]), bytes),
        "Second workspace principal can export its own package through the dedicated path.",
    )
    for actor, victim in (("alpha", "beta"), ("beta", "alpha")):
        before = backend.snapshot(principals[victim])
        result = backend.inspect_package(principals[actor], ids[victim]["package"])
        after = backend.snapshot(principals[victim])
        evidence.record(
            f"cross-workspace-package-{actor}-to-{victim}",
            result == SAFE_DENIAL,
            "Dedicated package path denies a known valid foreign project ID.",
        )
        evidence.record(
            f"cross-workspace-package-{actor}-to-{victim}-state-unchanged",
            before == after,
            "Denied package request leaves the victim workspace unchanged.",
        )

    backup_ids: dict[str, str] = {}
    for workspace, other in (("alpha", "beta"), ("beta", "alpha")):
        backup_id, backup = backend.backup(principals[workspace])
        backup_ids[workspace] = backup_id
        expected_ids = sorted(ids[workspace].values())
        evidence.record(
            f"backup-containment-{workspace}",
            sorted(item["id"] for item in backup["projects"]) == expected_ids
            and sorted(item["project_id"] for item in backup["history"]) == expected_ids
            and backup["evaluations"] == []
            and all(
                item["draft"]["visibility_lock"] == "permanent-private"
                and item["draft"]["bfs_firewall"] is True
                for item in backup["projects"]
            ),
            "Backup inventory exactly matches its workspace projects and privacy controls.",
        )
        evidence.record(
            f"own-backup-download-{workspace}",
            backend.download_backup(principals[workspace], backup_id).get("status") == 200,
            "Owning principal can retrieve its valid backup ID.",
        )
        before = backend.snapshot(principals[workspace])
        evidence.record(
            f"foreign-backup-download-{other}-to-{workspace}",
            backend.download_backup(principals[other], backup_id) == SAFE_DENIAL,
            "Foreign principal cannot retrieve another workspace's valid backup ID.",
        )
        evidence.record(
            f"foreign-backup-download-{other}-to-{workspace}-state-unchanged",
            before == backend.snapshot(principals[workspace]),
            "Denied backup download leaves the owner workspace unchanged.",
        )
        restored = backend.restore(principals[workspace], backup_id)
        evidence.record(
            f"restore-isolation-{workspace}",
            restored == {
                "status": 200, "isolated": True, "workspace": workspace,
                "location": f"restores/{workspace}/{backup_id}",
                "project_ids": expected_ids, "private": True,
            },
            "Restore reports a separate location with exact ownership and privacy-preserving inventory.",
        )
        evidence.record(
            f"foreign-backup-restore-{other}-to-{workspace}",
            backend.restore(principals[other], backup_id) == SAFE_DENIAL,
            "Another workspace cannot restore a valid foreign backup ID.",
        )
        for operation in OPERATIONS:
            own_key = f"own-{operation}"
            cross_key = f"cross-{operation}"
            own_result = backend.invoke_restored(
                principals[workspace], backup_id, operation, ids[workspace][own_key]
            )
            expected_status = 201 if operation == "duplicate" else 200
            evidence.record(
                f"restored-own-{workspace}-{operation}",
                own_result.get("status") == expected_status,
                "Owning principal successfully used its restored object through the tested path.",
            )
            before_foreign = backend.snapshot_restored(principals[workspace], backup_id)
            foreign_result = backend.invoke_restored(
                principals[other], backup_id, operation, ids[workspace][cross_key]
            )
            after_foreign = backend.snapshot_restored(principals[workspace], backup_id)
            evidence.record(
                f"restored-cross-workspace-{other}-to-{workspace}-{operation}",
                foreign_result == SAFE_DENIAL,
                "Foreign principal remains denied for the restored operation.",
            )
            evidence.record(
                f"restored-cross-workspace-{other}-to-{workspace}-{operation}-state-unchanged",
                before_foreign == after_foreign,
                "Denied restored operation leaves restored state unchanged.",
            )
            before_commingled = backend.snapshot_restored(principals[workspace], backup_id)
            commingled_result = backend.invoke_restored(
                principals[workspace], backup_id, operation, ids[other][cross_key]
            )
            after_commingled = backend.snapshot_restored(principals[workspace], backup_id)
            evidence.record(
                f"restored-owner-{workspace}-foreign-id-{operation}",
                commingled_result == SAFE_DENIAL,
                "Restored owner cannot access a known valid ID from another workspace.",
            )
            evidence.record(
                f"restored-owner-{workspace}-foreign-id-{operation}-state-unchanged",
                before_commingled == after_commingled,
                "Foreign-ID attempt leaves restored state unchanged.",
            )

    for operation in OPERATIONS:
        expected_status = 201 if operation == "duplicate" else 200
        own_key = f"own-{operation}"
        cross_key = f"cross-{operation}"
        for workspace in ("alpha", "beta"):
            own_result = backend.invoke(
                principals[workspace], operation, ids[workspace][own_key]
            )
            evidence.record(
                f"own-workspace-{workspace}-{operation}",
                own_result.get("status") == expected_status,
                "Authenticated principal successfully used its own valid object through the tested path.",
            )
        for actor, victim in (("alpha", "beta"), ("beta", "alpha")):
            before_foreign = backend.snapshot(principals[victim])
            result = backend.invoke(
                principals[actor], operation, ids[victim][cross_key]
            )
            after_foreign = backend.snapshot(principals[victim])
            evidence.record(
                f"cross-workspace-{actor}-to-{victim}-{operation}",
                result == SAFE_DENIAL,
                "Foreign valid ID received the same content-free not-found response.",
            )
            evidence.record(
                f"cross-workspace-{actor}-to-{victim}-{operation}-state-unchanged",
                before_foreign == after_foreign,
                "Denied foreign operation left projects, history, evaluations, and inventory unchanged.",
            )

    for actor, victim in (("alpha", "beta"), ("beta", "alpha")):
        before = backend.snapshot(principals[victim])
        result = backend.invoke_with_claimed_workspace(
            principals[actor], victim, "read", ids[victim]["own-read"]
        )
        evidence.record(
            f"confused-deputy-claimed-workspace-{actor}-to-{victim}",
            result == SAFE_DENIAL and before == backend.snapshot(principals[victim]),
            "A client-supplied workspace claim cannot redirect an authenticated operation.",
        )

    for workspace in ("alpha", "beta"):
        principal = principals[workspace]
        backend.revoke_session(principal)
        evidence.record(
            f"revoked-session-{workspace}",
            backend.invoke(principal, "read", ids[workspace]["own-read"])
            == SAFE_DENIAL,
            "A revoked session cannot access an owned object.",
        )
        backend.restore_session(principal, workspace)
        evidence.record(
            f"rotated-session-positive-control-{workspace}",
            backend.invoke(principal, "read", ids[workspace]["own-read"]).get("status")
            == 200,
            "A newly established session retains authorized same-workspace access.",
        )

    for workspace in ("alpha", "beta"):
        evidence.record(
            f"support-access-denied-{workspace}",
            backend.support_probe("provider-support", workspace) == SAFE_DENIAL,
            "Provider support has no standing workspace-data access path.",
        )

    for workspace in ("alpha", "beta"):
        backup_id = backup_ids[workspace]
        backend.expire(principals[workspace], backup_id)
        evidence.record(
            f"expired-backup-restore-{workspace}",
            backend.restore(principals[workspace], backup_id) == SAFE_DENIAL,
            "An expired backup cannot be restored.",
        )
        evidence.record(
            f"expired-backup-download-{workspace}",
            backend.download_backup(principals[workspace], backup_id) == SAFE_DENIAL,
            "An expired backup cannot be downloaded.",
        )
        evidence.record(
            f"retention-payload-deleted-{workspace}",
            backend.retention_status(principals[workspace], backup_id)
            == {"status": "deleted", "payload_present": False},
            "Retention evidence confirms the backup payload was removed.",
        )

    private_routes = [
        "/api/projects", f"/api/projects/{ids['alpha']['package']}",
        f"/api/projects/{ids['alpha']['package']}/export", "/api/backup",
        "/api/import", "/.foundry-data/workbench.sqlite", "/backups/latest",
        "/packages/latest.zip",
    ]
    for path in private_routes:
        evidence.record(
            f"unauthenticated-route-{path}",
            backend.unauthenticated_probe(path) == UNAUTHENTICATED_DENIAL,
            "Unauthenticated request receives a content-free authentication denial.",
        )
    inventory = backend.route_inventory()
    evidence.record(
        "private-route-inventory",
        bool(inventory)
        and all(item.get("auth_required") is True and item.get("public") is False for item in inventory),
        "Every inventoried authoring, package, backup, and restore route requires authentication.",
    )

    serialized_logs = json.dumps(backend.logs(), sort_keys=True)
    all_ids = [object_id for workspace_ids in ids.values() for object_id in workspace_ids.values()]
    evidence.record(
        "log-redaction",
        not any(marker in serialized_logs for marker in ("SOURCE_", "client-", "SESSION_SECRET", *all_ids)),
        "Audit evidence records workspace, operation, and outcome without object IDs or content.",
    )
    evidence.record(
        "cache-containment",
        backend.cache() == {"entries": 0, "private_payloads": []},
        "Reference adapter retains no private response cache.",
    )
    return evidence.report()


def add_public_artifact_proof(report: dict[str, Any], root: Path) -> dict[str, Any]:
    leaked: list[str] = []
    for directory in (root / "public", root / "dist" / "pages"):
        if not directory.is_dir():
            leaked.append(f"missing:{directory.relative_to(root)}")
            continue
        for path in directory.rglob("*"):
            if path.is_file() and any(marker in path.read_bytes() for marker in PUBLIC_FORBIDDEN):
                leaked.append(str(path.relative_to(root)))
    report["checks"].append({
        "claim": "public-artifact-containment",
        "status": "PASS" if not leaked else "FAIL",
        "detail": (
            "Public source and built artifacts contain no runtime, storage, credential, or private-route markers."
            if not leaked else f"Unsafe public artifact paths: {', '.join(leaked)}"
        ),
    })
    report["status"] = (
        "PASS" if all(item["status"] == "PASS" for item in report["checks"]) else "FAIL"
    )
    return report


def record_no_provider_decision(report: dict[str, Any]) -> dict[str, Any]:
    """Mark reference evidence as non-certifying when hosted use is declined."""

    reference_status = report["status"]
    report.update({
        "status": "BLOCKED",
        "proof_scope": "provider-independent-reference",
        "reference_contract_status": reference_status,
        "host_certification_status": "NOT_RUN",
        "selected_provider": None,
        "migration_authorized": False,
        "private_data_used": False,
        "decision": (
            "No hosted provider was selected. Hosted certification was not run, "
            "and existing local drafts remain unmigrated."
        ),
    })
    return report


def build_reference_proof() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp_dir:
        backend = ReferenceWorkspaceBackend(Path(temp_dir))
        backend.add_principal("principal-alpha", "alpha")
        backend.add_principal("principal-beta", "beta")
        ids: dict[str, dict[str, str]] = {"alpha": {}, "beta": {}}
        for workspace in ("alpha", "beta"):
            store = backend.add_workspace(workspace)
            fixture_labels = [
                label for operation in OPERATIONS
                for label in (f"own-{operation}", f"cross-{operation}")
            ] + ["package"]
            for label in fixture_labels:
                project = store.create(synthetic_draft(workspace.upper(), label))
                ids[workspace][label] = project["id"]
                backend.register(workspace, project["id"])
        return run_isolation_proof(
            backend,
            ids,
            {"alpha": "principal-alpha", "beta": "principal-beta"},
        )