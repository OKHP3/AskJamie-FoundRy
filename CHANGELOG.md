# Changelog

All notable changes to **AskJamie FoundRy** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [0.4.0] — 2026-06-04

### Added
- **Per-folder README / ABOUT files (11 new documents):**
  - `_template/ABOUT.md` — meta-description of the scaffold folder (preserving
    `_template/README.md` as the child-repo template placeholder)
  - `archive/README.md` — overview of both staged capabilities, graduation process
  - `assets/README.md` — shared brand assets structure and usage rules
  - `docs/README.md` — index of all 5 governance documents and workflows staging dir
  - `gpt-aj01-askjamie-resume-representative/README.md` — legacy folder orientation,
    redirect to canonical archive copy, AJ01 capability overview
  - `okhp3-brandguard-sentinel/README.md` — legacy folder orientation with BFS
    firewall notice, redirect to canonical archive copy, BRG00 capability overview
  - `registry/README.md` — registry table (9 repos), status values, how to add entries
  - `schemas/README.md` — schema summaries, validation commands, upgrade procedure
  - `scripts/README.md` — expanded to document all 7 scripts with usage examples

### Changed
- `README.md` — "Repository Structure" section replaced with "Repository Catalog":
  four subsections (Governance and Infrastructure, Capability Efforts Staged for
  Graduation, Legacy Folders, Root Files), each with links to per-folder READMEs.
- `assets/brand/README.md` — removed stale note about brand files being at root
  (they have been moved to `assets/brand/` and the root copies removed).

### Removed
- `askjamie-brand-standards.docx` (root) — duplicate of `assets/brand/` copy; removed.
- `askjamie-brand-standards.pdf` (root) — duplicate of `assets/brand/` copy; removed.

---

## [0.3.0] — 2026-06-04

### Added
- `scripts/normalize_filenames.py` — canonical filename normalization utility.
  Converts ™, —, é, &, ,, #, (, ), ' and other non-standard characters to
  ASCII-compliant kebab-case slugs. Supports dry-run (default) and `--apply`,
  `--recursive`, `--ascii-only`, `--include-dirs`, and `--exclude-path` flags.
  Fixed NFKD transliteration so accented letters (é → e) are retained rather
  than dropped. Preserves `PRESERVE_NAMES` list (README, CHANGELOG, AGENTS, etc.)
  and Windows-reserved basename guard.

### Changed
- **Full filename normalization pass — 74 renames applied across the repository.**
  All file and folder names now comply with GitHub and Replit naming best practices
  (ASCII only, kebab-case separators, no special shell/URL characters):
  - Root: `askjamie™-brand-standards.*` → `askjamie-brand-standards.*`
  - Legacy folder: `gpt-aj01-askjamie™-—-résumé-representative/` →
    `gpt-aj01-askjamie-resume-representative/`
  - Legacy folder: `OKHP3-BrandGaurd-Sentinel/` → `okhp3-brandguard-sentinel/`
    (also corrects "Gaurd" → "Guard" typo)
  - Legacy subfolder: `BFS-Framing-Intelligent-Futures/` →
    `bfs-framing-intelligent-futures/`
  - `archive/aj01-resume-representative/hr_guidebook_2025-(1).pdf` →
    `hr_guidebook_2025-1.pdf`
  - `archive/brg00-builders-firstsource/##-builders-firstsource-gpt-—-core.md` →
    `builders-firstsource-gpt-core.md`
  - All 32 knowledge files in `archive/brg00-builders-firstsource/knowledge/` and
    `okhp3-brandguard-sentinel/bfs-framing-intelligent-futures/knowledge/`:
    `&` → `and`, `,` → removed, `'` → removed, `—` → `-` in every filename.

---

## [0.2.0] — 2026-06-04

### Added
- `_template/` — complete child repo starter scaffold with all required files
  and directory structure per AGENTS.md §5.
- `registry/index.yaml` — authoritative catalog of all governed child repos.
- `registry/triage.md` — triage and intake log for new repo candidates.
- `schemas/manifest.schema.yaml` — YAML schema for child repo manifests.
- `schemas/registry.schema.yaml` — YAML schema for registry entries.
- `docs/relay-design.md` — relay architecture and design rationale.
- `docs/governance.md` — full governance reference for this FoundRy.
- `docs/naming-conventions.md` — naming rules and pattern reference.
- `docs/ecosystem-map.md` — visual and textual map of the OKHP3/AskJamie universe.
- `docs/migration-guide.md` — guide for migrating pre-standard repos.
- `.github/ISSUE_TEMPLATE/` — issue templates for capability requests, registry
  updates, governance changes, and bug reports.
- `.github/PULL_REQUEST_TEMPLATE.md` — standard PR checklist.
- `.github/workflows/validate-manifests.yml` — CI check for manifest schema.
- `.github/workflows/registry-lint.yml` — CI lint for registry index.
- `.github/CODEOWNERS` — code ownership assignments.
- `manifest.yaml` — self-describing manifest for this FoundRy relay.
- `LICENSE.md` — proprietary license declaration.
- `.gitignore` — comprehensive gitignore for the repo's toolchain.
- `.editorconfig` — editor consistency settings.
- `scripts/validate-manifest.py` — CLI tool for manifest schema validation.
- `scripts/check-registry.py` — CLI tool for registry health reporting.
- `assets/brand/` — directory for shared AskJamie™ brand assets.
- `archive/` — organized home for legacy and pre-standard content.

### Changed
- `README.md` — substantially expanded: ecosystem diagram, structure table,
  capability family index, quick-start instructions, and cross-links.
- `CHANGELOG.md` — reformatted to Keep a Changelog standard.
- Legacy content folders reorganized under `archive/` with proper READMEs.

---

## [0.1.0] — 2024-01-01

### Added
- Established FoundRy relay governance.
- Added repository purpose and inheritance model (`README.md`, `AGENTS.md`).
- Reserved template, registry, schema, and documentation structure in `AGENTS.md`.
- Initial `CHANGELOG.md`.

---

[Unreleased]: https://github.com/OKHP3/AskJamie-FoundRy/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/OKHP3/AskJamie-FoundRy/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/OKHP3/AskJamie-FoundRy/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/OKHP3/AskJamie-FoundRy/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/OKHP3/AskJamie-FoundRy/releases/tag/v0.1.0
