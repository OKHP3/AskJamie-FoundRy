# scripts/

**Role:** Python governance utilities for the AskJamie FoundRy relay.  
**Runtime:** Python 3.11 · PyYAML and jsonschema are pinned in `requirements.txt`
**Rule:** Do not place site-rendering scripts here unless this repo gains a deployable web surface.

---

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| [`validate-manifest.py`](validate-manifest.py) | Validate a `manifest.yaml` against `schemas/manifest.schema.yaml` | `python3 scripts/validate-manifest.py path/to/manifest.yaml` |
| [`check-registry.py`](check-registry.py) | Registry health check — validates `registry/index.yaml`, reports status summary and graduation candidates | `python3 scripts/check-registry.py` |
| [`normalize_filenames.py`](normalize_filenames.py) | Filename normalization — converts non-ASCII and non-standard characters to ASCII kebab-case | See below |
| [`manifest-audit.py`](manifest-audit.py) | Audit manifest fields across multiple repos for completeness and consistency | `python3 scripts/manifest-audit.py` |
| [`registry-audit.py`](registry-audit.py) | Extended registry audit — checks for orphaned entries, missing repos, or status inconsistencies | `python3 scripts/registry-audit.py` |
| [`foundry-sync.py`](foundry-sync.py) | Check sync posture between this FoundRy and known child repos | `python3 scripts/foundry-sync.py` |
| [`sync-report.py`](sync-report.py) | Generate a formatted sync status report for review | `python3 scripts/sync-report.py` |

---

## Quick Reference

### Validate a manifest

```bash
python3 scripts/validate-manifest.py manifest.yaml
# → ✅ PASS or detailed error output
```

### Check registry health

```bash
python3 scripts/check-registry.py
# → Summary table: total repos, by family/status, graduation candidates, locked repos
```

### Normalize filenames (dry run — no changes)

```bash
python3 scripts/normalize_filenames.py .
# Default: non-recursive, dry run. Shows what would be renamed.
```

### Normalize filenames (apply — recursive, ASCII only, including dirs)

```bash
python3 scripts/normalize_filenames.py . --recursive --ascii-only --include-dirs --apply
```

### Normalize a specific subtree only

```bash
python3 scripts/normalize_filenames.py archive/brg00-builders-firstsource --recursive --ascii-only --apply
```

---

## `normalize_filenames.py` — Full Options

```
usage: normalize_filenames.py [directory] [options]

positional:
  directory           Root path to scan (default: current directory)

options:
  --apply             Actually rename files (default: dry run)
  --recursive         Process all subfolders
  --ascii-only        Strip/transliterate non-ASCII characters
  --include-dirs      Also normalize directory names (deepest first)
  --include-hidden    Include hidden paths (names starting with '.')
  --include-default-dirs  Include _template, lib, artifacts (excluded by default)
  --exclude-path PATH Exclude a subtree (repeatable)
  --include-ext EXT   Only rename files with this extension (repeatable)
  --exclude-ext EXT   Skip files with this extension (repeatable)
```

**Preserved names** (never renamed): `README.md`, `CHANGELOG.md`, `AGENTS.md`,
`LICENSE.md`, `CODEOWNERS`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and other
GitHub-conventional ALLCAPS filenames.

---

## Related

- [`schemas/manifest.schema.yaml`](../schemas/manifest.schema.yaml) — schema used by `validate-manifest.py`
- [`schemas/registry.schema.yaml`](../schemas/registry.schema.yaml) — schema used by `check-registry.py`
- [`registry/index.yaml`](../registry/index.yaml) — registry validated by `check-registry.py`
