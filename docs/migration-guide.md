# Migration Guide — AskJamie FoundRy

This guide covers migrating pre-standard content and legacy-named repos into
the current AskJamie FoundRy governance structure.

---

## When to Use This Guide

Use this guide when:

- A folder or repository exists with a non-standard name.
- A repository is missing `manifest.yaml`, `AGENTS.md`, or other required files.
- Legacy content (GPT configs, knowledge packs, prompt files) exists outside
  of the proper directory structure.
- A repo was created before the current naming conventions were established.

---

## Migration Process

### Step 1 — Triage the Content

Add an entry to `registry/triage.md` describing what the content is, where
it currently lives, and what you propose to do with it.

```yaml
- name: [proposed-slug]
  source: [current folder or repo URL]
  intake_date: YYYY-MM-DD
  proposed_code: [aj## | brg##]
  proposed_family: [family]
  proposed_visibility: [private | public]
  decision: pending
  notes: ""
```

### Step 2 — Determine the Standard Home

| If the content is... | It should go to... |
|---|---|
| A fully-formed capability (prompts, knowledge, skill files) | A new child repo named per `docs/naming-conventions.md` |
| Draft/in-progress content | `archive/[code]-[slug]/` in this FoundRy, pending graduation |
| Retired or superseded content | `archive/[code]-[slug]/` — no graduation planned |
| Brand asset files (.pdf, .docx, logos) | `assets/brand/` in this FoundRy |

### Step 3 — Stage the Content

If the content is going to `archive/` in this FoundRy:

1. Create a subfolder: `archive/[code]-[slug]/`.
2. Move content into the subfolder.
3. Add a `README.md` to the subfolder explaining what it is, its origin,
   its current status, and its intended destination (if any).

If the content is graduating to its own repo:

1. Create the new repo on GitHub using the standard naming convention.
2. Copy `_template/` contents into the new repo.
3. Move/reorganize the legacy content into the proper directory structure
   (`origin/`, `skill/`, `prompts/`, `knowledge/`, etc.).
4. Fill in `manifest.yaml` with correct lineage, status, and visibility.
5. Add the new repo to `registry/index.yaml`.
6. Update `registry/triage.md` to mark the decision as resolved.

### Step 4 — Update the Registry

Whether the content is archived here or graduated to a new repo, update
`registry/index.yaml` with the correct entry and status.

### Step 5 — Validate

```bash
# If a manifest.yaml was created/updated:
python3 scripts/validate-manifest.py path/to/manifest.yaml

# Run registry health check:
python3 scripts/check-registry.py
```

---

## Known Legacy Content in This FoundRy

| Legacy Location | Standard Destination | Status |
|---|---|---|
| `gpt-aj01-askjamie™-—-résumé-representative/` | `archive/aj01-resume-representative/` → eventually `askjamie-aj01-resume-representative` repo | Staged in archive |
| `OKHP3-BrandGaurd-Sentinel/BFS-Framing-Intelligent-Futures/` | `archive/brg00-builders-firstsource/` → eventually `askjamie-brg00-builders-firstsource` repo | Staged in archive |
| `askjamie™-brand-standards.docx` / `.pdf` | `assets/brand/` | Move pending |

---

## File Renaming — Special Characters

Legacy file and folder names in this repo include special characters
(`™`, `é`, `—`, `&`, `#`). GitHub supports these but they can cause issues
with some tooling. When graduating content to a new repo:

- Rename files to use only ASCII characters, hyphens, and underscores.
- Preserve the original names in the archive/ copy for historical reference.
- Document the rename in the archive README.

Examples:
- `askjamie™-brand-standards.pdf` → `askjamie-brand-standards.pdf`
- `hr_guidebook_2025-(1).pdf` → `hr_guidebook_2025-v2.pdf`
- `##-builders-firstsource-gpt-—-core.md` → `builders-firstsource-gpt-core.md`

---

## Checklist for Migrated Repos

- [ ] Repo named per `docs/naming-conventions.md`
- [ ] `AGENTS.md` present and filled in
- [ ] `README.md` present and filled in
- [ ] `CHANGELOG.md` present
- [ ] `LICENSE.md` present
- [ ] `manifest.yaml` present and validates against schema
- [ ] Entry in `registry/index.yaml`
- [ ] `registry/triage.md` entry closed out
- [ ] No special characters in file/folder names (if new repo)
- [ ] No client-sensitive content in public-candidate repos
