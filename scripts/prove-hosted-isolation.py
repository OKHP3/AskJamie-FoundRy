#!/usr/bin/env python3
"""Print hosted-isolation status without implying provider certification."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.hosted_isolation_harness import (
    add_public_artifact_proof,
    build_reference_proof,
    record_no_provider_decision,
)


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/build-public-artifact.py", "--build"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    report = add_public_artifact_proof(build_reference_proof(), ROOT)
    report = record_no_provider_decision(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
