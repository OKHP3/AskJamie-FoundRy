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
ADAPTATION_ID = "read-only-regional-mentor-governance-audit"
ADAPTATION = {
    "id": ADAPTATION_ID,
    "name": "Read-only regional mentor governance audit",
    "boundary": (
        "Use the named mentor audit as evidence for a private AskJamie "
        "governance review. Do not copy a governance or graduation surface, "
        "publish a package, or host the authoring workbench."
    ),
    "publication_decision": "not-authorized",
    "hosting_decision": "not-authorized",
}
MENTOR_REVIEW = {
    "repository": "OKHP3/OverKill-Hill-FoundRy",
    "revision": "8de1eb212d8db193fd22eb85bf0843f366a0c1a7",
    "source_url": (
        "https://github.com/OKHP3/OverKill-Hill-FoundRy/blob/"
        "8de1eb212d8db193fd22eb85bf0843f366a0c1a7/"
        "scripts/public-graduation-audit.py"
    ),
    "path": "scripts/public-graduation-audit.py",
    "reviewed_at": "2026-09-17",
    "reviewer": "Replit Agent",
    "observation": (
        "The read-only dry-run checks release-package completeness, restricted "
        "references, record consistency, and manual disabled deployment; it "
        "does not grant publication approval or change repository visibility."
    ),
}


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
            "reason": "No owner decision record was supplied.",
        }
    try:
        approval = yaml.safe_load(approval_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return {
            "required": True,
            "status": "INVALID",
            "path": str(approval_path),
            "reason": f"Cannot read owner decision record: {exc}",
        }
    if not isinstance(approval, dict):
        return {
            "required": True,
            "status": "INVALID",
            "path": str(approval_path),
            "reason": "Owner decision record must be a YAML mapping.",
        }
    required = {
        "audit": AUDIT_NAME,
        "scope": AUDIT_SCOPE,
        "adaptation": ADAPTATION_ID,
        "owner": "OKHP3",
        "registry_sha256": registry_digest,
        "publication_decision": ADAPTATION["publication_decision"],
        "hosting_decision": ADAPTATION["hosting_decision"],
    }
    problems = [
        f"{key} does not match the required value"
        for key, expected in required.items()
        if approval.get(key) != expected
    ]
    decision = approval.get("decision")
    if decision not in {"approve", "defer", "reject"}:
        problems.append("decision must be approve, defer, or reject")
    decided_at = approval.get("decided_at", approval.get("approved_at"))
    try:
        date.fromisoformat(str(decided_at))
    except (TypeError, ValueError):
        problems.append("decided_at must be an ISO date")
    status_by_decision = {
        "approve": "APPROVED",
        "defer": "DEFERRED",
        "reject": "REJECTED",
    }
    status = status_by_decision.get(decision, "INVALID")
    return {
        "required": True,
        "status": status if not problems else "INVALID",
        "path": str(approval_path),
        "decision": decision,
        "decided_at": decided_at,
        "reason": (
            f"Exact scope, adaptation, registry digest, and release boundaries "
            f"recorded with decision: {decision}."
            if not problems
            else "; ".join(problems)
        ),
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
            "tier": "CONFIRMED",
            "evidence": [
                MENTOR_REVIEW["source_url"],
                f"revision:{MENTOR_REVIEW['revision']}",
                f"path:{MENTOR_REVIEW['path']}",
                f"reviewed_at:{MENTOR_REVIEW['reviewed_at']}",
                f"reviewer:{MENTOR_REVIEW['reviewer']}",
            ],
            "consequence_if_false": "AskJamie could adopt an inaccurate or obsolete pattern.",
            "next_check": "Review a later mentor revision before extending this observation.",
        },
        {
            "claim": "The proposed adaptation is safe for AskJamie regional boundaries.",
            "tier": "PROPOSAL",
            "evidence": ["docs/regional-governance-audit.md"],
            "consequence_if_false": "The adaptation could weaken local privacy or ownership controls.",
            "next_check": "Review the adaptation against the local workbench, export, and client controls.",
        },
        {
            "claim": "Owner decision exists for this exact adaptation, scope, and registry state.",
            "tier": "CONFIRMED"
            if approval["status"] in {"APPROVED", "DEFERRED", "REJECTED"}
            else "UNKNOWN",
            "evidence": [approval["path"]] if approval["path"] else [],
            "consequence_if_false": "A design review could be mistaken for authorization to adopt or publish.",
            "next_check": "Obtain or renew a dated owner decision tied to this adaptation, scope, registry digest, and release boundaries.",
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
        "adaptation": ADAPTATION,
        "evidence": evidence,
        "mentor_review": MENTOR_REVIEW,
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
            "The reviewed mentor behavior may differ in a later revision.",
            "Regional adaptation has not received implementation review.",
        ] + ([
            "Owner has not recorded a valid decision for this exact adaptation, scope, digest, and release boundary."
        ] if approval["status"] not in {"APPROVED", "DEFERRED", "REJECTED"} else []),
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
        help="Read an owner decision record tied to the adaptation, scope, and digest.",
    )
    parser.add_argument(
        "--require-approval",
        action="store_true",
        help="Fail unless a matching owner decision record is supplied.",
    )
    args = parser.parse_args()
    report = build_report(
        baseline_sha256=args.baseline_sha256,
        approval_path=args.owner_approval,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["audit"]["status"] == "FAIL":
        return 1
    if args.require_approval and report["owner_approval"]["status"] not in {
        "APPROVED",
        "DEFERRED",
        "REJECTED",
    }:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
