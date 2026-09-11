# AGENTS.md: AskJamie-FoundRy

## Project identity

This repository is the intentionally public AskJamie FoundRy relay. Its confirmed role is
to translate parent OKHP3 governance into child-repository scaffolds, schemas,
registry records, documentation, and staged capability assets.

It is a public-source development and governance workbench with a local single-user
application under `workbench/`. Python serves a plain HTML/CSS/JavaScript
interface and persists capability drafts and evaluation records in SQLite.
The application generates governed packages and executable decision tools.
It does not provision hosted agents or execute arbitrary generated code.

Authority flows in this direction:

```text
OKHP3/OverKill-Hill
  -> OKHP3/AskJamie-FoundRy
    -> AskJamie child repositories
```

The longer-term aim, inferred from the repository structure and migration
guides, is to mature reusable AskJamie capabilities here and graduate them to
governed child repositories without losing lineage or visibility controls.

## Scope and boundaries

This relay owns:

- `_template/`: the starter scaffold for child repositories
- `registry/`: the authoritative child-repository catalog and intake log
- `schemas/`: manifest and registry schemas
- `docs/`: relay design, governance, naming, migration, and ecosystem guidance
- `.github/`: repository metadata, pull-request guidance, and issue templates
- `.agents/skills/`: project-local Agent Skills and their evaluation resources
- `assets/`: shared AskJamie brand assets
- `public/`: read-only Pages orientation source, separate from private authoring
- `scripts/`: Python governance utilities
- `workbench/`: local application, static interface and public Skillz metadata snapshot
- `tests/`: application and governance regression checks

The compatibility workflow is active under `.github/workflows/`. Older workflow
examples under `docs/github-workflows/` remain reference files.
The Pages workflow is manually dispatched only; merging source does not
authorize publication. The manifest's `surface_boundary` separates public
orientation from the loopback workbench. Hosted authoring remains design-only.

This repository owns its local workbench runtime. It does not own sibling
application implementations, hosted production configuration, or public release
decisions. Do not infer that a registry entry proves a remote child repository
exists or is operational.

## Current status

Confirmed by `manifest.yaml`:

- Type: `foundry-relay`
- Lifecycle status: `active`
- Repository visibility: public
- Parent foundry: `OKHP3/OverKill-Hill`
- Parent FoundRy relay: `OKHP3/OverKill-Hill-FoundRy`

The registry contains nine governed child-repository entries. Earlier AJ01 and
BRG00 staged capability material was removed from this checkout on 2026-07-27.
The remaining entries are cataloged as planned or draft work unless their
registry status says otherwise.

## Repository structure and entry points

Read these files first when orienting to a task:

| Path | Use |
|---|---|
| `README.md` | Repository purpose, catalog, and working overview |
| `manifest.yaml` | This relay's identity, lineage, scope, and visibility |
| `registry/index.yaml` | Source of truth for governed child repositories |
| `registry/triage.md` | Candidate intake and archival decisions |
| `_template/ABOUT.md` | How to scaffold a child repository |
| `schemas/manifest.schema.yaml` | Child manifest contract |
| `schemas/registry.schema.yaml` | Registry entry contract |
| `docs/governance.md` | Governance rules and maintenance obligations |
| `docs/naming-conventions.md` | Repository and filename conventions |
| `docs/migration-guide.md` | Legacy-content and graduation procedure |
| `replit.md` | Replit-oriented project overview and access boundary |
| `CHANGELOG.md` | Material repository changes |

Capability repositories inherit this directory contract from `_template/`:

```text
docs/ origin/ skill/ prompts/ research/ tests/
schemas/ assets/ exports/ archive/
```

The root repository has no nested Git repositories or submodules. Historical
capability folders and their staged archive copies are no longer present in this
checkout.

## Runtime and validation

The application and utilities were verified under Python 3.11.15 and 3.14.5.
Older Windows launcher observations are historical and do not describe this Mac runtime. Runtime dependencies are pinned in `requirements.txt`: `PyYAML` for
YAML parsing and `jsonschema` for schema validation. The interface has no build step.
SQLite and HTTP support use the Python standard library.

Install `requirements.txt` into an activated virtual environment first, as
documented in `docs/workbench.md`. Verified baseline commands:

```bash
python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/check-registry.py
python3 scripts/build-public-artifact.py --build
python3 -m unittest discover -s tests -v
```

Start the app with `python3 -m workbench --port 8765`, then open
`http://127.0.0.1:8765`. It binds to loopback only. Private local state lives in
ignored `.foundry-data/`; use `--data-dir` to choose another private directory.
On POSIX systems the dedicated state directory is owner-only (0700), with
SQLite state files owner read/write (0600). This is not encryption or Windows
ACL management. Stop the server before copying its data directory for backup.
The application also supports versioned backup/import and confirmed project
duplication/deletion. Backup files contain private state and must remain private.

Run the validators after changing `manifest.yaml`, either schema,
`registry/index.yaml`, or the child template. Run the test suite after runtime,
validation, or export changes. See `docs/workbench.md` for the operating model.

The active compatibility workflow under `.github/workflows/` and the staged
workflow definitions under `docs/github-workflows/` install the pinned
dependencies from `requirements.txt`. The older staged definitions remain
reference files unless explicitly activated under `.github/workflows/`.

## Safe-change rules

- Preserve the parent-child lineage in every manifest and registry entry.
- Use the naming patterns in `docs/naming-conventions.md`.
- Update `registry/index.yaml` when a child relationship, status, visibility,
  or graduation decision changes.
- Update `CHANGELOG.md` for material governance, schema, template, or registry
  changes.
- Start new child repositories from `_template/`, then replace every template
  placeholder before publishing.
- Keep new filenames ASCII-only, lowercase where the naming guide requires it,
  and free of special punctuation.
- Do not commingle client-overlay content with public portfolio artifacts.
- Treat `client_org`, `bfs_firewall: true`, and
  `visibility_lock: permanent-private` as sensitive controls. Locked content
  must remain private.
- Public graduation is a registry decision. Do not change a visibility lock or
  graduation flag without explicit maintainer direction.
- Preserve standalone punchy lines in generated documentation. Concise prose
  is preferred, and extra explanation should earn its space.
- Do not use em dashes in generated content. Use a colon, comma, or a new
  sentence instead.
- AutoCAD version is R10. This constraint is locked and must not be changed or
  replaced in generated content.

## Known gaps and risks

These are repository findings, not assumptions:

- `scripts/foundry-sync.py` and `scripts/sync-report.py` are lightweight posture
  reports, not authoritative validators. The canonical paths are
  `registry/triage.md`, `schemas/manifest.schema.yaml`,
  `schemas/registry.schema.yaml`, and `docs/governance.md`.
- Registry checks now invoke `schemas/registry.schema.yaml` and enforce
  permanent-private restrictions. Draft exports include proposals; they never
  modify the authoritative registry automatically.
- `CLAUDE.md` is retained as a compatibility pointer because repository history
  mentions its deletion, but the file is present in the current checkout.
- The registry records planned child repositories, but this checkout does not
  establish their remote existence, deployment state, or ownership beyond the
  metadata recorded locally.

## Application and universe boundaries

The owner's 2026-09-07 direction establishes three overlapping regions:
AskJamie left, OverKill as centroid and baseline pattern, Glee-fully right.
The regional sites borrow from OverKill or defer to it when a question arises.
Skillz is shared. Intentionally public OverKill Found-Ry is the mentor pattern
for both regional Found-Rys, with reciprocal and peer mentoring encouraged.
Start from relevant mentor patterns, adapt to regional needs, and offer useful
improvements back through reviewable changes. Existing lineage is preserved;
mentoring does not require a shared application runtime. See `docs/ecosystem-map.md`.

- Keep all workbench projects and generated packages private by default.
- Never clear protection flags or client identity after a draft becomes protected.
- Treat selected Skillz metadata as references, not executable or verified skills.
- Label supplied-response checks distinctly from model execution; there are no
  model-provider calls in the local runtime.
- A valid package is not public graduation, a created remote repository, or an
  operational hosted assistant. Decision packages include an offline runner.
- Replit workspace parity and deployment require separate authenticated inspection.

## Cross-platform collaboration

Follow [the collaboration protocol](docs/agent-collaboration.md) for shared work
across ChatGPT/Codex, Claude, GitHub Copilot, and Replit. Keep AGENTS.md canonical;
platform-specific instruction files are pointers, not competing policies.

Use the owner's larger ChatGPT allocation for substantial implementation and
integration reasoning, Claude for bounded independent review when available,
Copilot for narrow code assistance, and Replit for workspace-specific execution
and validation. These are routing preferences, not automatic tool access or
permission to buy capacity. Minimize total token cost, accepting longer elapsed
time. Delegate only concrete independent work with explicit scope and evidence.

Before editing, claim a task in a shared GitHub issue or PR and record its owner,
base SHA, branch, affected paths, acceptance checks, and handoff status. One
integration owner controls each task branch and final merge. Other workers use
isolated branches or worktrees. Do not concurrently mutate a shared checkout.
If an existing Replit task is underway, coordinate with its owner before taking
over its files. A stale timestamp does not transfer ownership.

GitHub `main` requires a pull request and the supported Python validation check.
This is a solo-maintainer repository: the owner directed zero required external
approving reviews on 2026-09-10. Automated review is advisory. Follow the sync
procedure in `replit.md` for Replit
OAuth workflow-scope rejections. Preserve commits and use an already authorized
connection; never weaken protection or transfer credentials to repair a push.

All three Found-Ry source repositories are intentionally public by owner
confirmation. Private draft data and protected child capabilities remain
private. This task scope covers AskJamie-FoundRy only; Skillz is context, not
an additional assigned workstream.

## Keeping this guide current

When the repository structure, manifest contract, registry rules, validation
commands, or visibility policy changes, update this file together with the
affected schema, template, documentation, and `CHANGELOG.md`. Re-run the two
verified baseline commands and re-read this file before completing the change.

## Related repositories

- [OKHP3/AskJamie](https://github.com/OKHP3/AskJamie): public portfolio sibling
- [OKHP3/OverKill-Hill](https://github.com/OKHP3/OverKill-Hill): parent universe governance
- [OKHP3/OverKill-Hill-FoundRy](https://github.com/OKHP3/OverKill-Hill-FoundRy): parent relay
- [OKHP3/AskJamie-FoundRy](https://github.com/OKHP3/AskJamie-FoundRy): this repository
