from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
import io
from copy import deepcopy
from pathlib import Path

from tests.hosted_isolation_harness import (
    SAFE_DENIAL,
    ReferenceWorkspaceBackend,
    add_public_artifact_proof,
    build_reference_proof,
    record_no_provider_decision,
    run_isolation_proof,
    synthetic_draft,
)


ROOT = Path(__file__).resolve().parent.parent


class HostedIsolationProofTests(unittest.TestCase):
    def test_two_workspace_provider_contract_produces_reviewable_evidence(self):
        report = build_reference_proof()
        self.assertEqual(report["format"], "askjamie-hosted-isolation-proof")
        self.assertEqual(report["status"], "PASS", json.dumps(report, indent=2))
        claims = {item["claim"] for item in report["checks"]}
        for operation in (
            "read", "write", "history", "evaluate", "export", "duplicate", "delete",
        ):
            for workspace in ("alpha", "beta"):
                self.assertIn(f"own-workspace-{workspace}-{operation}", claims)
            for actor, victim in (("alpha", "beta"), ("beta", "alpha")):
                self.assertIn(f"cross-workspace-{actor}-to-{victim}-{operation}", claims)
                self.assertIn(
                    f"cross-workspace-{actor}-to-{victim}-{operation}-state-unchanged",
                    claims,
                )
        self.assertTrue({
            "package-containment", "backup-containment-alpha", "backup-containment-beta",
            "own-backup-download-alpha", "own-backup-download-beta",
            "foreign-backup-download-beta-to-alpha",
            "foreign-backup-download-alpha-to-beta",
            "restore-isolation-alpha", "restore-isolation-beta",
            "foreign-backup-restore-beta-to-alpha",
            "foreign-backup-restore-alpha-to-beta",
            "expired-backup-restore-alpha", "expired-backup-restore-beta",
            "expired-backup-download-alpha", "expired-backup-download-beta",
            "retention-payload-deleted-alpha", "retention-payload-deleted-beta",
            "private-route-inventory",
            "log-redaction", "cache-containment",
            "confused-deputy-claimed-workspace-alpha-to-beta",
            "confused-deputy-claimed-workspace-beta-to-alpha",
            "revoked-session-alpha", "revoked-session-beta",
            "rotated-session-positive-control-alpha",
            "rotated-session-positive-control-beta",
            "support-access-denied-alpha", "support-access-denied-beta",
        } <= claims)
        for workspace, other in (("alpha", "beta"), ("beta", "alpha")):
            for operation in (
                "read", "write", "history", "evaluate", "export", "duplicate", "delete",
            ):
                self.assertIn(f"restored-own-{workspace}-{operation}", claims)
                self.assertIn(
                    f"restored-cross-workspace-{other}-to-{workspace}-{operation}", claims
                )
                self.assertIn(
                    f"restored-cross-workspace-{other}-to-{workspace}-{operation}-state-unchanged",
                    claims,
                )
                self.assertIn(f"restored-owner-{workspace}-foreign-id-{operation}", claims)
                self.assertIn(
                    f"restored-owner-{workspace}-foreign-id-{operation}-state-unchanged",
                    claims,
                )
        for actor, victim in (("alpha", "beta"), ("beta", "alpha")):
            self.assertIn(f"cross-workspace-package-{actor}-to-{victim}", claims)

    def test_deny_all_adapter_cannot_pass_the_contract(self):
        class DenyAllBackend(ReferenceWorkspaceBackend):
            def invoke(self, principal, operation, object_id):
                return dict(SAFE_DENIAL)

        with tempfile.TemporaryDirectory() as temp_dir:
            backend = DenyAllBackend(Path(temp_dir))
            backend.add_principal("principal-alpha", "alpha")
            backend.add_principal("principal-beta", "beta")
            ids = {"alpha": {}, "beta": {}}
            for workspace in ("alpha", "beta"):
                store = backend.add_workspace(workspace)
                labels = [
                    label for operation in (
                        "read", "write", "history", "evaluate", "export",
                        "duplicate", "delete",
                    )
                    for label in (f"own-{operation}", f"cross-{operation}")
                ] + ["package"]
                for label in labels:
                    project = store.create(synthetic_draft(workspace.upper(), label))
                    ids[workspace][label] = project["id"]
                    backend.register(workspace, project["id"])
            report = run_isolation_proof(
                backend, ids,
                {"alpha": "principal-alpha", "beta": "principal-beta"},
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(
            item["claim"].startswith("own-workspace-") and item["status"] == "FAIL"
            for item in report["checks"]
        ))

    def test_unsafe_restore_and_commingled_data_cannot_pass(self):
        class UnsafeBackend(ReferenceWorkspaceBackend):
            def inspect_package(self, principal, object_id):
                original = super().inspect_package(principal, object_id)
                if not isinstance(original, bytes):
                    return original
                buffer = io.BytesIO()
                with zipfile.ZipFile(io.BytesIO(original)) as source, zipfile.ZipFile(buffer, "w") as target:
                    for name in source.namelist():
                        target.writestr(name, source.read(name))
                    target.writestr("leaked-project-id.txt", self.leaked_id)
                    target.writestr("content-only-leak.txt", b"SOURCE_BETA_READ_PRIVATE")
                return buffer.getvalue()

            def backup(self, principal):
                backup_id, backup = super().backup(principal)
                if self.sessions[principal] == "alpha":
                    backup = deepcopy(backup)
                    foreign = self.stores["beta"].backup()["projects"][0]
                    backup["projects"].append(foreign)
                    self.backups[backup_id] = ("alpha", backup, False)
                return backup_id, backup

            def restore(self, principal, backup_id):
                if self.sessions[principal] == "alpha":
                    return {"status": 200}
                return super().restore(principal, backup_id)

            def invoke_restored(self, principal, backup_id, operation, object_id):
                if self.sessions[principal] == "beta" and operation == "export":
                    return {"status": 200, "bytes": 1}
                return super().invoke_restored(principal, backup_id, operation, object_id)

            def download_backup(self, principal, backup_id):
                result = super().download_backup(principal, backup_id)
                if self.sessions[principal] == "alpha" and result == SAFE_DENIAL:
                    return {"status": 200, "backup": {}}
                return result

            def expire(self, principal, backup_id):
                owner, backup, _ = self.backups[backup_id]
                self.backups[backup_id] = (owner, backup, True)

            def unauthenticated_probe(self, path):
                if path == "/api/backup":
                    return {"status": 200, "backup": {}}
                return super().unauthenticated_probe(path)

            def invoke_with_claimed_workspace(
                self, principal, claimed_workspace, operation, object_id
            ):
                if self.sessions.get(principal) == "alpha" and claimed_workspace == "beta":
                    return {"status": 200, "id": object_id}
                return super().invoke_with_claimed_workspace(
                    principal, claimed_workspace, operation, object_id
                )

            def revoke_session(self, principal):
                if principal != "principal-alpha":
                    super().revoke_session(principal)

            def support_probe(self, support_actor, workspace_id):
                if workspace_id == "alpha":
                    return {"status": 200}
                return super().support_probe(support_actor, workspace_id)

            def invoke(self, principal, operation, object_id):
                if (
                    self.sessions[principal] == "alpha"
                    and self.owners.get(object_id) == "beta"
                    and operation == "write"
                ):
                    store = self.stores["beta"]
                    project = store.get(object_id)
                    draft = {
                        key: value for key, value in project.items()
                        if key not in {
                            "id", "revision", "created_at", "updated_at",
                            "visibility", "public_graduation_allowed",
                        }
                    }
                    store.update(object_id, project["revision"], draft)
                    return dict(SAFE_DENIAL)
                return super().invoke(principal, operation, object_id)

        with tempfile.TemporaryDirectory() as temp_dir:
            backend = UnsafeBackend(Path(temp_dir))
            backend.add_principal("principal-alpha", "alpha")
            backend.add_principal("principal-beta", "beta")
            ids = {"alpha": {}, "beta": {}}
            for workspace in ("alpha", "beta"):
                store = backend.add_workspace(workspace)
                labels = [
                    label for operation in (
                        "read", "write", "history", "evaluate", "export",
                        "duplicate", "delete",
                    )
                    for label in (f"own-{operation}", f"cross-{operation}")
                ] + ["package"]
                for label in labels:
                    project = store.create(synthetic_draft(workspace.upper(), label))
                    ids[workspace][label] = project["id"]
                    backend.register(workspace, project["id"])
            backend.leaked_id = ids["alpha"]["own-read"]
            report = run_isolation_proof(
                backend, ids,
                {"alpha": "principal-alpha", "beta": "principal-beta"},
            )
        failed = {item["claim"] for item in report["checks"] if item["status"] == "FAIL"}
        self.assertTrue({
            "package-containment", "backup-containment-alpha", "restore-isolation-alpha",
            "restored-cross-workspace-beta-to-alpha-export",
            "expired-backup-download-alpha", "retention-payload-deleted-alpha",
            "unauthenticated-route-/api/backup",
            "cross-workspace-alpha-to-beta-write-state-unchanged",
            "confused-deputy-claimed-workspace-alpha-to-beta",
            "revoked-session-alpha",
            "support-access-denied-alpha",
        } <= failed)

    def test_public_artifacts_contain_no_private_or_runtime_markers(self):
        subprocess.run(
            ["python3", "scripts/build-public-artifact.py", "--build"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        forbidden = (
            b"SOURCE_ALPHA_PRIVATE", b"SOURCE_BETA_PRIVATE", b"client-alpha-private",
            b"client-beta-private", b"SQLite format 3", b"SESSION_SECRET",
            b".foundry-data", b"workbench.sqlite", b"/api/", b"localStorage",
            b"sessionStorage", b"fetch(",
        )
        for directory in (ROOT / "public", ROOT / "dist" / "pages"):
            for path in directory.rglob("*"):
                if path.is_file():
                    payload = path.read_bytes()
                    for marker in forbidden:
                        self.assertNotIn(marker, payload, f"{marker!r} leaked into {path}")
        report = add_public_artifact_proof(build_reference_proof(), ROOT)
        self.assertEqual(report["checks"][-1]["claim"], "public-artifact-containment")
        self.assertEqual(report["checks"][-1]["status"], "PASS")

    def test_no_provider_decision_cannot_be_mistaken_for_certification(self):
        reference = build_reference_proof()
        report = record_no_provider_decision(deepcopy(reference))

        self.assertEqual(reference["status"], "PASS")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["reference_contract_status"], "PASS")
        self.assertEqual(report["host_certification_status"], "NOT_RUN")
        self.assertIsNone(report["selected_provider"])
        self.assertFalse(report["migration_authorized"])
        self.assertFalse(report["private_data_used"])


if __name__ == "__main__":
    unittest.main()