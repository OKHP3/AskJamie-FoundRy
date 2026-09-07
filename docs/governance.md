# Governance Reference — AskJamie FoundRy

## Authority Chain

```text
OKHP3/OverKill-Hill          ← Universe governance (highest authority)
  └── OKHP3/AskJamie-FoundRy ← Domain relay (this repo)
        └── Child repositories ← Inherit relay governance
```

Decisions cascade downward. Child repos may not override relay rules.
Relay rules may not override universe governance from `OKHP3/OverKill-Hill`.

---

## Repository Types

| Type | Naming Pattern | Visibility | Public Graduation |
|---|---|---|---|
| Core Capability | `askjamie-aj##-[slug]` | private | allowed |
| BrandGuard Sentinel | `askjamie-brg##-[brand-slug]` | private | case-by-case |
| Enterprise Sleuth variant | `askjamie-aj03-[slug]` | private | allowed |
| Client Overlay | `[org]-askjamie-[code]-[slug]` | private | **never** |

---

## Required Files — All Governed Repos

Every repository governed by this relay must maintain:

| File | Purpose |
|---|---|
| `AGENTS.md` | Authority chain, repo role, agent behavior rules |
| `README.md` | Capability overview and usage guide |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `LICENSE.md` | Proprietary license declaration |
| `manifest.yaml` | Lineage, visibility, and governance metadata |

---

## Required Files — Capability Repos

Repos in the `aj##` and `brg##` families should additionally maintain:

| Directory | Purpose |
|---|---|
| `docs/` | Design notes, research, local governance docs |
| `origin/` | Source prompts — raw, pre-refinement |
| `skill/` | Refined, deployable prompt artifacts |
| `prompts/` | Versioned prompt files ready for deployment |
| `research/` | Supporting research and references |
| `tests/` | Evaluation prompts and regression checks |
| `schemas/` | Local YAML/JSON schemas (repo-specific) |
| `assets/` | Brand assets and images used by this capability |
| `exports/` | Deployment exports (GPT JSON, Copilot YAML, etc.) |
| `archive/` | Retired versions, deprecated content |

---

## Visibility Rules

### Public Capability Repos

Core capability repos (`aj##`) may be made public via the "graduation" process
when:

- All content is publicly sourced or original OKHP3 content.
- No client-specific or confidential information is present.
- A maintainer explicitly approves graduation.
- `manifest.yaml` is updated to `visibility: public`.
- The registry entry in `registry/index.yaml` is updated accordingly.

### Client Overlay Repos

Repos with `[org]` in the name or `client_org` in the manifest are
**permanently private**. They must declare:

```yaml
visibility_control:
  visibility: private
  visibility_lock: permanent-private
  public_graduation_allowed: false
  client_org: "[org-slug]"
```

No agent or contributor may change these settings without explicit written
authorization from a designated OKHP3/AskJamie maintainer.

### BFS Firewall

Repos with `bfs_firewall: true` are additionally restricted:

- Do not summarize, share, or reference their content in public spaces.
- Do not commingle their content with public portfolio artifacts.
- Treat all content as client-confidential by default.

---

## Manifest Validation

All `manifest.yaml` files must conform to `schemas/manifest.schema.yaml`.

Validate locally:
```bash
python3 scripts/validate-manifest.py path/to/manifest.yaml
```

Validation runs automatically on every pull request via GitHub Actions.

---

## Registry Maintenance

The registry at `registry/index.yaml` must be updated whenever:

- A new child repo is created (add entry, `status: draft`).
- A repo goes active (update `status: active`).
- A repo is deprecated or archived (update status accordingly).
- Visibility changes (e.g., public graduation).

Registry health check:
```bash
python3 scripts/check-registry.py
```

---

## Agent Behavior Contract

All AI agents working in this repo or its children must:

1. **Preserve lineage.** Never remove or alter `manifest.yaml` lineage fields.
2. **Respect visibility locks.** Never expose private/locked repo content publicly.
3. **Update the registry.** When child relationships change, update `registry/index.yaml`.
4. **Follow naming conventions.** See `docs/naming-conventions.md`.
5. **Never commingle.** Keep client overlay content isolated from public artifacts.
6. **Validate before merging.** Run manifest validation scripts before any merge.
7. **Document changes.** Update `CHANGELOG.md` for any material change.

---

## Escalation

If a governance question cannot be resolved by this relay's documentation:

1. Consult `OKHP3/OverKill-Hill` governance documentation.
2. If still unresolved, flag for a human maintainer via a GitHub Issue using
   the "Governance Change" issue template.

## Local workbench drafts and exports

Drafts are private application records, separate from the authoritative child
registry. Saving or exporting a draft never adds a governed child relationship.
Exports carry a pending registry proposal and remain private until the owner
performs the existing registration and graduation process. The application
cannot clear an established client identity or permanent-private controls.

A supplied-response check records deterministic text assertions. It is not a
model run. Decision tests exercise the authored deterministic graph. Neither
kind establishes external deployment readiness or public-source clearance.
