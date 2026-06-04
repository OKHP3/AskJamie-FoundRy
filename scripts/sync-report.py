#!/usr/bin/env python3
from __future__ import annotations
import datetime
import pathlib

ROOT = pathlib.Path('.')
CHECKS = ['AGENTS.md','README.md','CHANGELOG.md','manifest.yaml','_template/AGENTS.md','_template/manifest.yaml','registry/index.yaml','schemas/repo-manifest.schema.yaml','scripts/foundry-sync.py']

print('# FoundRy Sync Report')
print()
print(f'Generated: {datetime.date.today().isoformat()}')
print()
for path in CHECKS:
    status = 'OK' if (ROOT / path).exists() else 'MISSING'
    print(f'- {status}: `{path}`')
