#!/usr/bin/env python3
"""Audit a FoundRy manifest.yaml for required governance fields."""
from __future__ import annotations
import pathlib
import re
import sys

REQUIRED_TOKENS = ["schema_version:", "repo:", "name:", "display_name:", "type:", "lifecycle_status:", "visibility:", "brand_domain:", "author:"]
VALID_STATUSES = {"spark", "research", "concept", "prototype", "capability", "productizing", "product", "active", "archived", "deprecated"}

def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def value(text: str, key: str) -> str:
    m = re.search(rf"^\s*{re.escape(key)}:\s*\"?([^\n\"]*)\"?\s*$", text, re.M)
    return m.group(1).strip() if m else ""

def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    path = root / "manifest.yaml"
    if not path.exists():
        print("FAIL manifest.yaml missing")
        return 1
    text = read(path)
    missing = [t for t in REQUIRED_TOKENS if t not in text]
    if missing:
        print("FAIL missing required manifest tokens:")
        for item in missing:
            print(f"  - {item}")
        return 1
    status = value(text, "lifecycle_status")
    if status and status not in VALID_STATUSES:
        print(f"WARN lifecycle_status not in known set: {status}")
    print("OK manifest.yaml baseline fields present")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
