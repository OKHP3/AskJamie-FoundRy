"""Evidence, protection, and immutability checks for the regional audit."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "regional_governance_audit",
    ROOT / "scripts" / "regional-governance-audit.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RegionalGovernanceAuditTests(unittest.TestCase):
    def copy_fixture(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "registry").mkdir()
        (root / "schemas").mkdir()
        (root / "scripts").mkdir()
        (root / "registry/index.yaml").write_text(
            (ROOT / "registry/index.yaml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "schemas/registry.schema.yaml").write_text(
            (ROOT / "schemas/registry.schema.yaml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "scripts/check-registry.py").write_text(
            (ROOT / "scripts/check-registry.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        return root

    def test_clean_report_passes_controls_but_defers_adoption(self):
        report = MODULE.build_report(ROOT)
        self.assertEqual(report["audit"]["status"], "PASS")
        self.assertEqual(report["audit"]["adoption"], "DEFERRED")
        self.assertEqual(report["owner_approval"]["status"], "PENDING")
        self.assertTrue(report["registry"]["unchanged_during_audit"])
        self.assertEqual(report["protected_client_records"]["violations"], [])
        tiers = {item["claim"]: item["tier"] for item in report["evidence"]}
        self.assertEqual(
            tiers["The named OverKill mentor surface has the stated governance or graduation behavior."],
            "UNKNOWN",
        )

    def test_baseline_digest_is_required_to_match(self):
        digest = hashlib.sha256(
            (ROOT / "registry/index.yaml").read_bytes()
        ).hexdigest()
        self.assertEqual(
            MODULE.build_report(ROOT, baseline_sha256=digest)["audit"]["status"],
            "PASS",
        )
        self.assertEqual(
            MODULE.build_report(ROOT, baseline_sha256="0" * 64)["audit"]["status"],
            "FAIL",
        )

    def test_protected_record_sweep_catches_visibility_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_fixture(tmp)
            registry_path = root / "registry/index.yaml"
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            data["repositories"][8]["visibility"] = "public"
            registry_path.write_text(yaml.safe_dump(data), encoding="utf-8")
            report = MODULE.build_report(root)
            self.assertEqual(report["audit"]["status"], "FAIL")
            self.assertTrue(report["protected_client_records"]["violations"])

    def test_approval_must_match_scope_and_registry_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_fixture(tmp)
            registry_digest = hashlib.sha256(
                (root / "registry/index.yaml").read_bytes()
            ).hexdigest()
            approval = {
                "audit": MODULE.AUDIT_NAME,
                "scope": MODULE.AUDIT_SCOPE,
                "decision": "approve",
                "owner": "OKHP3",
                "approved_at": "2026-09-14",
                "registry_sha256": registry_digest,
            }
            approval_path = root / "approval.yaml"
            approval_path.write_text(yaml.safe_dump(approval), encoding="utf-8")
            report = MODULE.build_report(root, approval_path=approval_path)
            self.assertEqual(report["owner_approval"]["status"], "APPROVED")

            changed = copy.deepcopy(approval)
            changed["scope"] = "public-graduation"
            approval_path.write_text(yaml.safe_dump(changed), encoding="utf-8")
            report = MODULE.build_report(root, approval_path=approval_path)
            self.assertEqual(report["owner_approval"]["status"], "INVALID")


if __name__ == "__main__":
    unittest.main()