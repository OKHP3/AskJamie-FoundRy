#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
REGISTRY = ROOT / 'registry' / 'index.yaml'

if not REGISTRY.exists():
    print('FAIL registry/index.yaml missing')
    raise SystemExit(1)

text = REGISTRY.read_text(encoding='utf-8', errors='replace')

required = ['schema_version:', 'repositories:']
missing = [r for r in required if r not in text]

if missing:
    print('FAIL missing registry markers')
    for item in missing:
        print(' -', item)
    raise SystemExit(1)

print('OK registry baseline valid')
