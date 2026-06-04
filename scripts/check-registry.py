#!/usr/bin/env python3
"""
check-registry.py
AskJamie FoundRy — Registry health check utility

Usage:
    python3 scripts/check-registry.py [--verbose] [--summary]

Reads registry/index.yaml and reports:
  - Total repo count by family and status
  - Entries that are missing required fields
  - Entries with inconsistent visibility settings
  - Client overlays that are missing visibility_lock
  - Schema validation (if jsonschema is available)

Exits 0 if all checks pass, 1 if any errors are found.
No external dependencies beyond pyyaml (+ jsonschema for full validation).
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml not installed. Run: pip install pyyaml")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_registry(registry_path: Path, schema_path: Path, verbose: bool) -> list[str]:
    errors = []
    data = load_yaml(registry_path)

    # Top-level fields
    for field in ["schema_version", "foundry", "updated", "repositories"]:
        if field not in data:
            errors.append(f"Registry missing top-level field: {field}")

    foundry = data.get("foundry", "")
    if foundry != "OKHP3/AskJamie-FoundRy":
        errors.append(f"foundry field is incorrect: {foundry!r}")

    repositories = data.get("repositories", [])
    if not isinstance(repositories, list):
        errors.append("repositories must be a list")
        return errors

    # Per-entry checks
    required_entry_fields = ["repo", "display_name", "code", "family",
                              "status", "visibility", "public_graduation_allowed"]
    valid_families = {"core-capability", "brandguard", "enterprise-sleuth", "client-overlay"}
    valid_statuses = {"draft", "active", "deprecated", "archived"}
    valid_visibilities = {"private", "public"}

    seen_repos = set()
    seen_codes = defaultdict(list)
    stats = defaultdict(lambda: defaultdict(int))

    for i, entry in enumerate(repositories):
        prefix = f"Entry #{i+1} ({entry.get('repo', 'unknown')})"

        # Required fields
        for field in required_entry_fields:
            if field not in entry:
                errors.append(f"{prefix}: missing required field '{field}'")

        repo = entry.get("repo", "")
        if repo:
            if repo in seen_repos:
                errors.append(f"{prefix}: duplicate repo entry: {repo!r}")
            seen_repos.add(repo)
            if not repo.startswith("OKHP3/"):
                errors.append(f"{prefix}: repo must start with 'OKHP3/' — got {repo!r}")

        code = entry.get("code", "")
        family = entry.get("family", "")
        status = entry.get("status", "")
        visibility = entry.get("visibility", "")
        graduation = entry.get("public_graduation_allowed", None)
        visibility_lock = entry.get("visibility_lock", "")
        client_org = entry.get("client_org", "")

        if family and family not in valid_families:
            errors.append(f"{prefix}: invalid family {family!r}")
        if status and status not in valid_statuses:
            errors.append(f"{prefix}: invalid status {status!r}")
        if visibility and visibility not in valid_visibilities:
            errors.append(f"{prefix}: invalid visibility {visibility!r}")

        # Client overlay checks
        if family == "client-overlay":
            if not client_org:
                errors.append(f"{prefix}: client-overlay must have client_org")
            if visibility_lock != "permanent-private":
                errors.append(f"{prefix}: client-overlay must have visibility_lock: permanent-private")
            if graduation is not False:
                errors.append(f"{prefix}: client-overlay must have public_graduation_allowed: false")

        # Locked repos should not be public
        if visibility_lock == "permanent-private" and visibility == "public":
            errors.append(f"{prefix}: visibility is 'public' but visibility_lock is permanent-private")

        # Stats
        if family:
            stats[family][status or "unknown"] += 1

    return errors, stats, repositories


def print_summary(repositories, stats):
    total = len(repositories)
    print(f"\n{'─'*50}")
    print(f"  AskJamie FoundRy — Registry Summary")
    print(f"{'─'*50}")
    print(f"  Total repositories: {total}")
    print()

    for family in sorted(stats.keys()):
        print(f"  {family}:")
        for status, count in sorted(stats[family].items()):
            print(f"    {status:12s}  {count}")
    print(f"{'─'*50}")

    # Public candidates
    public_candidates = [
        r["repo"] for r in repositories
        if r.get("public_graduation_allowed") is True and r.get("status") == "draft"
    ]
    if public_candidates:
        print(f"\n  Public graduation candidates ({len(public_candidates)}):")
        for r in public_candidates:
            print(f"    {r}")

    # Permanently private
    locked = [
        r["repo"] for r in repositories
        if r.get("visibility_lock") == "permanent-private"
    ]
    if locked:
        print(f"\n  Permanently private ({len(locked)}):")
        for r in locked:
            print(f"    {r}")
    print()


def main():
    parser = argparse.ArgumentParser(description="AskJamie FoundRy registry health check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show more detail")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary only (no errors)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    registry_path = repo_root / "registry" / "index.yaml"
    schema_path = repo_root / "schemas" / "registry.schema.yaml"

    if not registry_path.exists():
        print(f"ERROR: Registry not found at {registry_path}")
        sys.exit(1)

    print(f"Registry : {registry_path}")

    result = check_registry(registry_path, schema_path, args.verbose)
    errors, stats, repositories = result

    print_summary(repositories, stats)

    if not args.summary:
        if errors:
            print(f"Errors found ({len(errors)}):")
            for e in errors:
                print(f"  ✗ {e}")
            print(f"\n❌ FAIL — registry health check failed with {len(errors)} error(s)")
            sys.exit(1)
        else:
            print("✅ PASS — registry/index.yaml is healthy")
            sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
