#!/usr/bin/env python3
"""Run the evidence and protection gate for a regional governance audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry" / "index.yaml"
SCHEMA = ROOT / "schemas" / "registry.schema.yaml"
AUDIT_NAME = "askjamie-regional-governance"
AUDIT_SCOPE = "broader-mentor-governance-and-graduation"


def load_registry_checker():
    path = ROOT / "scripts" / "check-registry.py"
    spec = importlib.util.spec_from_file_location("registry_checker", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load registry validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_violations(repositories: list[dict[str, Any]]) -> list[str]:
    violations: list[str] = []
    for index, entry in enumerate(repositories, start=1):
        if not isinstance(entry, dict):
            continue
        protected = (
            entry.get("family") == "client-overlay"
            or bool(entry.get("client_org"))
            or entry.get("bfs_firewall") is True
            or entry.get("visibility_lock") == "permanent-private"
        )
        if not protected:
            continue
        label = f"entry-{index}"
        if entry.get("visibility") != "private":
            violations.append(f"{label}: protected entry is not private")
        if entry.get("public_graduation_allowed") is not False:
            violations.append(f"{label}: protected entry allows public graduation")
        if entry.get("visibility_lock") != "permanent-private":
            violations.append(f"{label}: protected entry lacks permanent-private lock")
    return violations


def approval_status(
    approval_path: Path | None,
    registry_digest: str,
) -> dict[str, Any]:
    if approval_path is None:
        return {
            "required": True,
            "status": "PENDING",
            "path": None,
            "reason": "No owner approval record was supplied.",
        }
    try:
        approval = yaml.safe_load(approval_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return {
            "required": True,
            "status": "INVALID",
            "path": str(approval_path),
            "reason": f"Cannot read approval record: {exc}",
        }
    required = {
        "audit": AUDIT_NAME,
        "scope": AUDIT_SCOPE,
        "decision": "approve",
        "owner": "OKHP3",
        "registry_sha256": registry_digest,
    }
    problems = [
        f"{key} does not match the required value"
        for key, expected in required.items()
        if approval.get(key) != expected
    ]
    approved_at = approval.get("approved_at")
    try:
        date.fromisoformat(str(approved_at))
    except (TypeError, ValueError):
        problems.append("approved_at must be an ISO date")
    return {
        "required": True,
        "status": "APPROVED" if not problems else "INVALID",
        "path": str(approval_path),
        "reason": "Exact scope and registry digest approved."
        if not problems
        else "; ".join(problems),
    }


def build_report(
    root: Path = ROOT,
    *,
    baseline_sha256: str | None = None,
    approval_path: Path | None = None,
) -> dict[str, Any]:
    registry_path = root / "registry" / "index.yaml"
    schema_path = root / "schemas" / "registry.schema.yaml"
    before = registry_path.read_bytes()
    before_digest = hashlib.sha256(before).hexdigest()

    checker = load_registry_checker()
    errors, stats, repositories = checker.check_registry(
        registry_path, schema_path, False
    )
    after = registry_path.read_bytes()
    after_digest = hashlib.sha256(after).hexdigest()
    unchanged = before == after
    baseline_matches = baseline_sha256 is None or before_digest == baseline_sha256
    violations = protected_violations(repositories)
    approval = approval_status(approval_path, before_digest)

    local_controls_pass = not errors and not violations and unchanged and baseline_matches
    evidence = [
        {
            "claim": "AskJamie registry passes the canonical schema and health checks.",
            "tier": "CONFIRMED" if not errors else "UNKNOWN",
            "evidence": [
                "scripts/check-registry.py",
                "schemas/registry.schema.yaml",
            ],
            "consequence_if_false": "Registry relationships may be malformed or unsafe to review.",
            "next_check": "Correct the validator failure in a separate reviewed change.",
        },
        {
            "claim": "Protected client and BFS records remain private and graduation-disabled.",
            "tier": "CONFIRMED" if not violations else "UNKNOWN",
            "evidence": ["regional audit protected-record sweep"],
            "consequence_if_false": "Client or firewall-protected material could be exposed or promoted.",
            "next_check": "Stop and review the named protected record without copying its content.",
        },
        {
            "claim": "The registry did not change during the audit.",
            "tier": "CONFIRMED" if unchanged and baseline_matches else "UNKNOWN",
            "evidence": [f"sha256:{before_digest}"],
            "consequence_if_false": "The evidence may describe a different registry state than the reviewed state.",
            "next_check": "Restart from a clean, owner-approved registry snapshot.",
        },
        {
            "claim": "The named OverKill mentor surface has the stated governance or graduation behavior.",
            "tier": "UNKNOWN",
            "evidence": [],
            "consequence_if_false": "AskJamie could adopt an inaccurate or obsolete pattern.",
            "next_check": "Review the exact mentor source revision, path, and primary evidence.",
        },
        {
            "claim": "The proposed adaptation is safe for AskJamie regional boundaries.",
            "tier": "PROPOSAL",
            "evidence": ["docs/regional-governance-audit.md"],
            "consequence_if_false": "The adaptation could weaken local privacy or ownership controls.",
            "next_check": "Review the adaptation against the local workbench, export, and client controls.",
        },
        {
            "claim": "Owner approval exists for this exact adoption scope and registry state.",
            "tier": "CONFIRMED" if approval["status"] == "APPROVED" else "UNKNOWN",
            "evidence": [approval["path"]] if approval["path"] else [],
            "consequence_if_false": "A design review could be mistaken for authorization to adopt or publish.",
            "next_check": "Obtain a dated owner decision tied to this scope and registry digest.",
        },
    ]
    return {
        "audit": {
            "name": AUDIT_NAME,
            "schema_version": "1.0",
            "region": "AskJamie",
            "mentor": "OKHP3/OverKill-Hill-FoundRy",
            "scope": AUDIT_SCOPE,
            "mode": "design",
            "status": "PASS" if local_controls_pass else "FAIL",
            "adoption": "DEFERRED",
        },
        "evidence": evidence,
        "registry": {
            "path": str(registry_path.relative_to(root)),
            "sha256": before_digest,
            "unchanged_during_audit": unchanged,
            "baseline_sha256": baseline_sha256,
            "baseline_matches": baseline_matches,
            "canonical_validator_errors": errors,
        },
        "protected_client_records": {
            "count": sum(
                1
                for entry in repositories
                if isinstance(entry, dict)
                and (
                    entry.get("family") == "client-overlay"
                    or bool(entry.get("client_org"))
                    or entry.get("bfs_firewall") is True
                    or entry.get("visibility_lock") == "permanent-private"
                )
            ),
            "violations": violations,
        },
        "owner_approval": approval,
        "remaining_unknowns": [
            "Exact mentor source revision and governance surface are not recorded.",
            "Regional adaptation has not received implementation review.",
            "Owner has not approved adoption of this exact scope and digest.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-sha256",
        help="Require registry/index.yaml to match this pre-audit digest.",
    )
    parser.add_argument(
        "--owner-approval",
        type=Path,
        help="Read an owner approval record tied to the audit scope and digest.",
    )
    parser.add_argument(
        "--require-approval",
        action="store_true",
        help="Fail unless a matching owner approval record is supplied.",
    )
    args = parser.parse_args()
    report = build_report(
        baseline_sha256=args.baseline_sha256,
        approval_path=args.owner_approval,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["audit"]["status"] == "FAIL":
        return 1
    if args.require_approval and report["owner_approval"]["status"] != "APPROVED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())