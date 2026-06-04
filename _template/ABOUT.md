# _template/ — Child Repository Scaffold

**Role:** Canonical starter scaffold for every new AskJamie child repository.  
**Owner:** OKHP3/AskJamie-FoundRy (this relay)  
**Governed by:** [`AGENTS.md`](../AGENTS.md) §5 — Required Child Repo Files

---

## Purpose

`_template/` is the single source of truth for the required structure of any
AskJamie child repo. When a new capability, BrandGuard Sentinel, or client
overlay is created, it starts from a copy of this folder.

> **Rule:** Never scaffold a child repo by hand. Always copy from `_template/`.

---

## What the Template Contains

| File / Folder | Purpose in the Child Repo |
|---|---|
| `README.md` | Placeholder README with fill-in-the-blank sections |
| `AGENTS.md` | Placeholder authority chain and agent behavior contract |
| `CHANGELOG.md` | Placeholder changelog (Keep a Changelog format) |
| `LICENSE.md` | Proprietary license declaration |
| `manifest.yaml` | Placeholder manifest with all required lineage fields |
| `docs/` | Design notes, governance references, research |
| `origin/` | Raw source material (GPT system prompts, interview notes, unrefined drafts) |
| `skill/` | Refined, reusable capability artifacts |
| `prompts/` | Versioned, deployment-ready prompt files |
| `research/` | Supporting research, competitive analysis, reference material |
| `tests/` | Evaluation prompts, regression checks, behavioral test cases |
| `schemas/` | Local YAML/JSON schemas specific to the child repo |
| `assets/` | Brand assets and images local to this capability |
| `exports/` | Deployment exports (GPT JSON config, Copilot YAML, Gem YAML, etc.) |
| `archive/` | Retired versions and deprecated content within the child repo |

Empty directories contain a `.gitkeep` file so they are tracked by git.

---

## How to Use This Template

### Step 1 — Copy the scaffold

```bash
cp -r _template/ ../[new-repo-name]/
cd ../[new-repo-name]/
```

Or copy via GitHub's "Use this template" flow if the relay is ever configured
as a GitHub Template Repository.

### Step 2 — Replace all placeholders

Every placeholder is wrapped in square brackets: `[DISPLAY_NAME]`, `[REPO_NAME]`,
`[aj## | brg##]`, `YYYY-MM-DD`, etc.

Required replacements in `manifest.yaml`:

```yaml
identity.repo:         OKHP3/[REPO_NAME]
identity.display_name: "[DISPLAY_NAME]"
identity.slug:         "[capability-slug]"
identity.type:         core-capability | brandguard | client-overlay | ...
brand.capability_code: aj## | brg##
```

### Step 3 — Register the new repo

Add an entry to [`registry/index.yaml`](../registry/index.yaml) in this FoundRy.

### Step 4 — Validate the manifest

```bash
python3 scripts/validate-manifest.py path/to/new-repo/manifest.yaml
```

---

## Template Governance

The template is versioned alongside the FoundRy. When the parent
(`OKHP3/OverKill-Hill`) publishes new governance standards:

1. Update the files in `_template/` to match.
2. Bump the FoundRy version in `CHANGELOG.md`.
3. Add triage entries for any child repos that need backfilling.

---

## Related

- [`registry/index.yaml`](../registry/index.yaml) — register new repos here
- [`docs/naming-conventions.md`](../docs/naming-conventions.md) — naming rules
- [`docs/migration-guide.md`](../docs/migration-guide.md) — bringing legacy repos up to standard
- [`schemas/manifest.schema.yaml`](../schemas/manifest.schema.yaml) — manifest validation schema
