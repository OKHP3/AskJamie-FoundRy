#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/check-registry.py
python3 -m unittest discover -s tests -v