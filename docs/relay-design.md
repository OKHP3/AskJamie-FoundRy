# Relay Design — AskJamie FoundRy

## Purpose

The AskJamie FoundRy combines a **governance relay** with a local authoring
application. Its governance role occupies the
middle layer of the OKHP3 governance hierarchy, translating golden standards
from the parent (`OKHP3/OverKill-Hill`) into actionable scaffolds, schemas,
and registry entries that child repositories inherit.

```text
OKHP3/OverKill-Hill          ← Universe-level governance (golden standards)
  └── OKHP3/AskJamie-FoundRy ← Relay (this repo) — translates and distributes
        ├── askjamie-aj##-*   ← Core capability repos (inherit from relay)
        ├── askjamie-brg##-*  ← BrandGuard repos (inherit from relay)
        └── [org]-askjamie-*  ← Client overlays (inherit, restricted)
```

---

## Relay Responsibilities

### 1. Scaffold Distribution (`_template/`)

The `_template/` directory contains the canonical starting point for every
new AskJamie child repository. When a new capability is created:

1. Copy `_template/` into the new repository.
2. Replace all `[PLACEHOLDER]` values with actual capability metadata.
3. Fill `manifest.yaml` with correct lineage and visibility settings.
4. Register the new repo in `registry/index.yaml`.

The template is the single source of truth for required file structure.
Never create a child repo by hand without starting from `_template/`.

### 2. Registry Maintenance (`registry/`)

`registry/index.yaml` is the authoritative catalog of all governed child
repositories. It must be kept in sync as repos are created, activated,
deprecated, or archived.

`registry/triage.md` is the intake log for content or repos that are being
evaluated but not yet formally registered.

### 3. Schema Ownership (`schemas/`)

This relay owns the canonical schemas for `manifest.yaml` and
`registry/index.yaml`. Any change to the schema must:

- Increment the `schema_version` field if it is a breaking change.
- Update all known child repo manifests if a required field is added.
- Be documented in `CHANGELOG.md`.

### 4. Governance Documentation (`docs/`)

The `docs/` directory contains the relay's authoritative governance
documentation. This includes naming rules, migration guides, ecosystem maps,
and this design document. Child repos may reference these docs but should not
duplicate them.

### 5. GitHub Automation (`.github/`)

GitHub Actions workflows in `.github/workflows/` validate manifests and
registry entries automatically on every pull request. Issue templates guide
contributors to provide the right information for common operations (new
capability requests, registry updates, governance changes).

---

## Design Principles

### Lineage First

Every artifact in the AskJamie ecosystem must declare its lineage in
`manifest.yaml`. The lineage chain (`parent_foundry`, `parent_repo`,
optionally `parent_capability`) is how the relay understands the dependency
graph and enforces governance.

### Durable Assets, Ephemeral Surfaces

The capability architecture — prompts, reasoning frameworks, knowledge packs,
conversation design — is the durable asset. Platform deployments (Custom GPTs,
Copilots, Gems, APIs) are ephemeral surfaces. A repo that only contains
a GPT configuration JSON with no backing skill files has not captured the
durable asset.

### Separation of Public and Private

Client overlay repos (`[org]-askjamie-*`) and BrandGuard sentinels with
`bfs_firewall: true` are permanently private and must never be commingled
with public portfolio artifacts. The registry makes this explicit via
`visibility_lock: permanent-private`.

### Registry as Source of Truth

The registry is authoritative over GitHub's own repository list. A repo that
exists on GitHub but is not in `registry/index.yaml` is not formally governed.
A registry entry without a corresponding GitHub repo is a planned/draft item.

---

## Governance Upgrade Path

When the parent FoundRy (`OKHP3/OverKill-Hill`) publishes new governance
standards, the relay's upgrade path is:

1. Pull the updated standards into `docs/governance.md`.
2. Update `_template/` to reflect any new required files or fields.
3. Update `schemas/` if the manifest schema changes.
4. Add entries to `registry/triage.md` for child repos that need updating.
5. Bump the relay's version in `CHANGELOG.md`.
6. Notify child repo maintainers via GitHub Discussions or issue creation.

## Local application layer

The owner authorized a working application on 2026-09-07. The runtime consumes
the existing template and schemas, saves draft projects separately from the
registry, and produces private packages plus proposed registration records.
This extends the relay role without treating an export as a child repository
creation or public graduation. See [workbench guide](workbench.md).

Skillz supplies shared public contract metadata. Intentionally public OverKill
Found-Ry supplies the mentor pattern for both regional Found-Rys. AskJamie and
Glee-fully can adapt that baseline, mentor each other, and contribute improvements
back to OverKill Found-Ry. Regional ownership and runtimes remain distinct.
