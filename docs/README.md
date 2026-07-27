# docs/

**Role:** Authoritative governance and design documentation for the AskJamie FoundRy relay.  
**Owner:** OKHP3/AskJamie-FoundRy  
**Rule:** Child repos may reference these documents but should not duplicate them.

---

## Contents

| File / Folder | Purpose |
|---|---|
| [`relay-design.md`](relay-design.md) | Architecture and design rationale for this relay layer |
| [`governance.md`](governance.md) | Full governance reference — roles, rules, and obligations |
| [`naming-conventions.md`](naming-conventions.md) | Canonical naming patterns for repos, files, and folders |
| [`migration-guide.md`](migration-guide.md) | How to bring legacy or pre-standard repos up to spec |
| [`ecosystem-map.md`](ecosystem-map.md) | Visual and textual map of the OKHP3 / AskJamie universe |
| [`askjamie-repository-inventory.md`](askjamie-repository-inventory.md) | Scoped crosswalk of AskJamie child repositories, local clones, and remote-name reconciliation |
| [`github-workflows/`](github-workflows/README.md) | Staged GitHub Actions workflows — pending activation |

---

## Document Summaries

### `relay-design.md`

Explains the relay architecture: how this FoundRy sits between the parent
universe (`OKHP3/OverKill-Hill`) and the child capability repos, what it owns,
and the design principles (lineage-first, durable assets over ephemeral surfaces,
registry as source of truth).

**Read this first** if you are new to the AskJamie FoundRy.

### `governance.md`

The full governance reference. Covers authority chain, contributor obligations,
schema ownership, visibility rules, and upgrade paths when the parent FoundRy
publishes new standards.

### `naming-conventions.md`

Canonical patterns for:
- Core capability repos (`askjamie-aj##-[slug]`)
- BrandGuard Sentinel repos (`askjamie-brg##-[slug]`)
- Client overlay repos (`[client-org]-askjamie-[code]-[slug]`)
- File and folder names within repos (ASCII only, kebab-case)

### `migration-guide.md`

Step-by-step guide for:
- Graduating archived content into a new standalone repo
- Bringing a legacy repo up to the current standard
- Backfilling a `manifest.yaml` into an existing repo

### `ecosystem-map.md`

A structured map of the entire OKHP3 / AskJamie universe: parent repos, sibling
FoundRies, public portfolio, deployment surfaces, and known child repos.

### `askjamie-repository-inventory.md`

Read-only snapshot of the scoped AskJamie child repositories and adjacent local
clones. Records canonical remote names, local origin naming, clone state, and
the boundary for future cross-repository interrogation or change work.

### `github-workflows/`

Staged CI/CD workflow YAML files pending activation in `.github/workflows/`.
See [`github-workflows/README.md`](github-workflows/README.md) for activation
instructions (requires a GitHub token with `workflow` scope).

---

## Updating These Documents

1. Edit the relevant `.md` file directly.
2. If the change affects required fields or schemas, also update `schemas/`.
3. If the change affects the `_template/`, update the scaffold.
4. Record the change in the root `CHANGELOG.md`.

---

## Related

- [`AGENTS.md`](../AGENTS.md) — authority chain and agent behavior rules
- [`schemas/`](../schemas/README.md) — YAML schema definitions
- [`_template/`](../_template/ABOUT.md) — child repo scaffold
