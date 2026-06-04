# Changelog

All notable changes to **AskJamie FoundRy** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

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

[Unreleased]: https://github.com/OKHP3/AskJamie-FoundRy/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/OKHP3/AskJamie-FoundRy/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/OKHP3/AskJamie-FoundRy/releases/tag/v0.1.0
