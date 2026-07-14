# AGENTS.md: AskJamie-FoundRy

## Project identity

This repository is the private AskJamie FoundRy relay. Its confirmed role is
to translate parent OKHP3 governance into child-repository scaffolds, schemas,
registry records, documentation, and staged capability assets.

It is a development and governance workbench, not a deployable application.
The repository has no server, frontend, backend, or application build. Its
runtime surface is limited to small Python governance utilities.

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
- `archive/`: legacy capability material staged for graduation
- `assets/`: shared AskJamie brand assets
- `scripts/`: Python governance utilities

The staged GitHub Actions workflow files are under
`docs/github-workflows/`. They are not currently active under
`.github/workflows/`.

This repository does not own deployed application code, production service
configuration, child-repository application implementations, or public release
decisions. Do not infer that a registry entry proves a remote child repository
exists or is operational.

## Current status

Confirmed by `manifest.yaml`:

- Type: `foundry-relay`
- Lifecycle status: `active`
- Visibility: private
- Parent foundry: `OKHP3/OverKill-Hill`
- Parent FoundRy relay: `OKHP3/OverKill-Hill-FoundRy`

The registry contains nine governed child-repository entries. Two capabilities
have local staged material under `archive/`: AJ01 Resume Representative and
BRG00 Builders FirstSource BrandGuard. The remaining entries are cataloged as
planned or draft work unless their registry status says otherwise.

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
| `replit.md` | Replit-oriented project overview and non-app status |
| `CHANGELOG.md` | Material repository changes |

Capability repositories inherit this directory contract from `_template/`:

```text
docs/ origin/ skill/ prompts/ research/ tests/
schemas/ assets/ exports/ archive/
```

The root repository has no nested Git repositories or submodules. The legacy
root folders `gpt-aj01-askjamie-resume-representative/` and
`okhp3-brandguard-sentinel/` remain for historical continuity. Their canonical
staged copies are under `archive/`.

## Runtime and validation

The utilities are documented for Python 3.11. Current verification ran under
Python 3.14.5. YAML parsing requires `pyyaml`; full manifest schema validation
uses `jsonschema` when available. `jsonschema` is not installed in the current
environment, so the manifest check used its structural fallback. There is no
package manager, application build, test suite, or local deployment command in
this repository.

Verified baseline commands:

```bash
python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/check-registry.py
```

Both commands pass in the current checkout. Run them after changing
`manifest.yaml`, either schema, `registry/index.yaml`, or the child template.

The staged workflow definitions in `docs/github-workflows/` install `pyyaml`
and `jsonschema` in CI. They are reference files until explicitly activated
under `.github/workflows/`.

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

- `scripts/manifest-audit.py` checks legacy fields such as `name`,
  `lifecycle_status`, and `author`, which are not part of the current manifest
  schema. Its current baseline run fails and should not be treated as the
  canonical manifest check.
- `scripts/foundry-sync.py` and `scripts/sync-report.py` still reference older
  paths including `registry/triage-log.md`,
  `schemas/repo-manifest-schema.yaml`, `schemas/repo-manifest.schema.yaml`,
  and `docs/governance-model.md`. The current paths are `registry/triage.md`,
  `schemas/manifest.schema.yaml`, and `docs/governance.md`.
- `scripts/check-registry.py` performs its own registry checks but does not
  invoke `schemas/registry.schema.yaml`, despite the surrounding documentation
  describing schema validation.
- `CLAUDE.md` is retained as a compatibility pointer because repository history
  mentions its deletion, but the file is present in the current checkout.
- The registry records planned child repositories, but this checkout does not
  establish their remote existence, deployment state, or ownership beyond the
  metadata recorded locally.

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
