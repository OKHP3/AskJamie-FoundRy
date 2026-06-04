#!/usr/bin/env python3
"""FoundRy sync posture audit.

Checks the local FoundRy relay repository for the baseline files and folders
required by the OKHP3 Tier 0 -> Tier 1 -> Tier 2 governance model.

Usage:
  python3 scripts/foundry-sync.py
  python3 scripts/foundry-sync.py --strict
"""

from __future__ import annotations

import argparse
import pathlib
import sys

REQUIRED_PATHS = [
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "manifest.yaml",
    "_template",
    "registry",
    "schemas",
    "docs",
    ".github",
]

RECOMMENDED_PATHS = [
    "scripts",
    "registry/index.yaml",
    "registry/triage-log.md",
    "schemas/repo-manifest-schema.yaml",
    "docs/governance-model.md",
]


def exists(root: pathlib.Path, rel_path: str) -> bool:
    return (root / rel_path).exists()


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit FoundRy relay sync posture.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to audit.")
    parser.add_argument("--strict", action="store_true", help="Fail when recommended paths are missing.")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    missing_required = [p for p in REQUIRED_PATHS if not exists(root, p)]
    missing_recommended = [p for p in RECOMMENDED_PATHS if not exists(root, p)]

    print("FoundRy sync posture audit")
    print(f"Root: {root}")
    print()

    if missing_required:
        print("Missing required paths:")
        for path in missing_required:
            print(f"  - {path}")
    else:
        print("Required paths: OK")

    if missing_recommended:
        print("\nMissing recommended paths:")
        for path in missing_recommended:
            print(f"  - {path}")
    else:
        print("Recommended paths: OK")

    if missing_required:
        return 1
    if args.strict and missing_recommended:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
