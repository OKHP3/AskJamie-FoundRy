# AskJamie Found-Ry project overview

Private AskJamie capability-building application and governance workbench.
The local application authors assistant specifications, decision tools and
workflows; saves SQLite drafts; records evaluations; and exports governed ZIPs.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 -m workbench --port 8765
```

Open http://127.0.0.1:8765. See [operating guide](docs/workbench.md).
The server is loopback-only. Existing Replit project metadata is retained;
its remote workspace, Run behavior and deployment were not verified during
this implementation. Replit preview hosting requires an authenticated access
design and separate parity check, not just binding this private server publicly.

## Ownership

AskJamie is the interpretation region. OverKill is the connective center.
Glee-fully is the personal-tools region. Skillz is shared across all three;
each regional Found-Ry owns its own fabrication line. Historical parent
metadata is provenance. See [ecosystem map](docs/ecosystem-map.md).

## Working contracts

- `AGENTS.md`: canonical agent and governance instructions.
- `workbench/`: Python runtime, static interface and public catalog snapshot.
- `_template/`, `schemas/`, `registry/`: authoritative scaffold/governance assets.
- `tests/`: runtime and validation regression checks.
- `.foundry-data/`: ignored private local state.

Preserve visibility locks, client isolation, lineage, and the locked AutoCAD
R10 constraint. Exports are private packages with pending registry proposals.
No automatic repository creation, publication or graduation occurs.
