# AskJamie Found-Ry project overview

Public-source AskJamie capability-building application and governance workbench.
Local drafts and protected exports remain private.
The local application authors assistant specifications, decision tools and
workflows; saves SQLite drafts; records evaluations; and exports governed ZIPs.

## Surface boundary

`public/` is a separately scoped, read-only Pages orientation artifact. It
communicates AskJamie’s relationship to OverKill Hill, Glee-fully, and shared
Skillz, and uses only relative assets. It never reads the local API, SQLite,
`.foundry-data/`, drafts, client records, secrets, or generated packages.

The authoring workbench is a Python standard-library/SQLite application bound to
`127.0.0.1`. It is not hosted in Replit preview or deployment. Public repository
visibility proves source visibility only, not hosted capability operation.
The hosted boundary is documented in
[docs/hosted-authoring-boundary.md](docs/hosted-authoring-boundary.md) and is
design-only. It does not authorize a workflow, hosted database, authentication
connector, provider call, telemetry service, or upload of `.foundry-data/`,
backups, client records, or generated packages.

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
- `docs/parity-matrix.md`: evidence-led mentor parity decisions.

Preserve visibility locks, client isolation, lineage, and the locked AutoCAD
R10 constraint. Exports are private packages with pending registry proposals.
No automatic repository creation, publication or graduation occurs.

## Collaboration across agent platforms

Read [AGENTS.md](AGENTS.md) and [the collaboration protocol](docs/agent-collaboration.md).
Continue existing assigned reconciliation work before starting another task.
Share a compact checkpoint through its GitHub issue or PR so ChatGPT/Codex,
Claude, or Copilot can take a bounded part without repeating the whole task.
Replit remains the executor for checks that require its actual workspace.
A GitHub merge alone does not prove this workspace has pulled the change.
