#!/usr/bin/env python3
"""
validate-manifest.py
AskJamie FoundRy — Manifest validation utility

Usage:
    python3 scripts/validate-manifest.py path/to/manifest.yaml
    python3 scripts/validate-manifest.py  # validates ./manifest.yaml

Validates a manifest.yaml against schemas/manifest.schema.yaml.
Exits 0 on success, 1 on failure. No external dependencies beyond
the standard library + pyyaml + jsonschema (pip install pyyaml jsonschema).

For environments without jsonschema, falls back to structural checks only.
"""

import sys
import os
import re
from pathlib import Path


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml is not installed. Run: pip install pyyaml")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_with_jsonschema(manifest: dict, schema: dict, manifest_path: str) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return []  # Fall through to structural checks

    errors = []
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        path = " → ".join(str(p) for p in error.path) if error.path else "(root)"
        errors.append(f"  [{path}] {error.message}")
    return errors


def structural_checks(manifest: dict, manifest_path: str) -> list[str]:
    """Lightweight structural checks — no jsonschema required."""
    errors = []

    required_top = ["schema_version", "identity", "brand", "lineage",
                    "governance", "visibility_control", "maintainers",
                    "created", "updated"]
    for field in required_top:
        if field not in manifest:
            errors.append(f"  Missing required field: {field}")

    identity = manifest.get("identity", {})
    for field in ["repo", "display_name", "slug", "type", "status"]:
        if field not in identity:
            errors.append(f"  identity.{field} is missing")

    repo = identity.get("repo", "")
    if repo and not repo.startswith("OKHP3/"):
        errors.append(f"  identity.repo must start with 'OKHP3/' — got: {repo!r}")

    slug = identity.get("slug", "")
    if slug and not re.match(r"^[a-z0-9-]+$", slug):
        errors.append(f"  identity.slug must be lowercase alphanumeric+hyphens — got: {slug!r}")

    valid_types = {"core-capability", "brandguard", "enterprise-sleuth",
                   "client-overlay", "conversation-design", "rag-experiment", "foundry-relay"}
    t = identity.get("type", "")
    if t and t not in valid_types:
        errors.append(f"  identity.type invalid: {t!r} (valid: {sorted(valid_types)})")

    valid_statuses = {"draft", "active", "deprecated", "archived"}
    s = identity.get("status", "")
    if s and s not in valid_statuses:
        errors.append(f"  identity.status invalid: {s!r} (valid: {sorted(valid_statuses)})")

    lineage = manifest.get("lineage", {})
    parent = lineage.get("parent_foundry", "")
    repo_type = identity.get("type", "")
    if parent and repo_type != "foundry-relay" and parent != "OKHP3/AskJamie-FoundRy":
        errors.append(f"  lineage.parent_foundry must be 'OKHP3/AskJamie-FoundRy' — got: {parent!r}")
    elif parent and repo_type == "foundry-relay" and not parent.startswith("OKHP3/"):
        errors.append(f"  lineage.parent_foundry must start with 'OKHP3/' — got: {parent!r}")

    vc = manifest.get("visibility_control", {})
    visibility_lock = vc.get("visibility_lock", "")
    graduation_allowed = vc.get("public_graduation_allowed", None)
    if visibility_lock == "permanent-private" and graduation_allowed is not False:
        errors.append("  visibility_control: if visibility_lock is 'permanent-private', "
                       "public_graduation_allowed must be false")

    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for date_field in ["created", "updated"]:
        val = manifest.get(date_field, "")
        if val and not date_pattern.match(str(val)):
            errors.append(f"  {date_field} must be ISO 8601 (YYYY-MM-DD) — got: {val!r}")

    maintainers = manifest.get("maintainers", [])
    if not maintainers:
        errors.append("  maintainers must have at least one entry")

    return errors


def main():
    # Determine manifest path
    if len(sys.argv) > 1:
        manifest_path = Path(sys.argv[1])
    else:
        manifest_path = Path("manifest.yaml")

    if not manifest_path.exists():
        print(f"ERROR: File not found: {manifest_path}")
        sys.exit(1)

    # Find schema relative to this script
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    schema_path = repo_root / "schemas" / "manifest.schema.yaml"

    print(f"Manifest : {manifest_path}")
    print(f"Schema   : {schema_path}")

    manifest = load_yaml(manifest_path)
    errors = []

    # Try jsonschema first
    if schema_path.exists():
        schema = load_yaml(schema_path)
        errors = validate_with_jsonschema(manifest, schema, str(manifest_path))
        if errors:
            print("\nSchema validation errors:")
            for e in errors:
                print(e)
        else:
            # Always run structural checks too
            errors = structural_checks(manifest, str(manifest_path))
            if errors:
                print("\nStructural check errors:")
                for e in errors:
                    print(e)
    else:
        print(f"NOTE: Schema not found at {schema_path}, running structural checks only.")
        errors = structural_checks(manifest, str(manifest_path))
        if errors:
            print("\nStructural check errors:")
            for e in errors:
                print(e)

    if errors:
        print(f"\n❌ FAIL — {len(errors)} error(s) found in {manifest_path}")
        sys.exit(1)
    else:
        print(f"\n✅ PASS — {manifest_path} is valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
