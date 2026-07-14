# AskJamie FoundRy — Project Overview

## Purpose

This is the private R&D and governance workbench for the **AskJamie™** ecosystem.
It is not a deployable application. It is a knowledge-and-governance fabrication
line: a place where capabilities are designed, tempered, and staged before being
exposed through public-facing deployment surfaces.

## Ecosystem Role

```
OKHP3/OverKill-Hill         ← Parent universe governance
  └── OKHP3/AskJamie-FoundRy ← This project (relay FoundRy)
        ├── askjamie-aj##-* ← Core capability repos
        ├── askjamie-brg##-* ← BrandGuard repos
        └── [org]-askjamie-* ← Client overlay repos (private)
```

## Three-Way Pairing

| Layer | Public | Private Workbench |
|---|---|---|
| Website | askjamie.bot | — |
| GitHub | OKHP3/AskJamie | OKHP3/AskJamie-FoundRy |
| Replit | AskJamie (portfolio) | AskJamie-FoundRy (this project) |

## Key Files & Directories

| Path | Purpose |
|---|---|
| `AGENTS.md` | Authority chain and AI agent behavior rules |
| `manifest.yaml` | Self-describing FoundRy manifest |
| `registry/index.yaml` | Authoritative catalog of all child repos |
| `_template/` | Starter scaffold for new child repos |
| `schemas/` | YAML schema definitions |
| `docs/` | Governance, naming, ecosystem, and migration guides |
| `.github/` | Repository metadata, issue templates, and PR guidance |
| `docs/github-workflows/` | Staged workflow definitions, not currently active |
| `archive/` | Staged legacy content pending graduation |
| `assets/brand/` | Shared AskJamie™ brand assets |
| `scripts/` | Python governance utilities |

## Governance Scripts

```bash
# Validate a manifest.yaml
python3 scripts/validate-manifest.py path/to/manifest.yaml

# Check registry health
python3 scripts/check-registry.py
```

## No Runnable Application

This project has no server, frontend, or backend. There is no workflow to start.
The "Run" button is not used. All work is documentation, governance artifacts,
and utility scripts.

## User Preferences

- Follow AskJamie FoundRy naming conventions (`docs/naming-conventions.md`) at all times.
- Treat any repo/content with `bfs_firewall: true` or `visibility_lock: permanent-private` as confidential.
- Never commingle client overlay content with public portfolio artifacts.
- Keep `registry/index.yaml` and `CHANGELOG.md` up to date with any material change.
- Use Keep a Changelog format for all CHANGELOG.md files.
- All file/folder names in new repos should use ASCII only (no ™, é, —, &, ##).
- When creating a new child repo, always start from `_template/`.
- Validate manifests before merging any PR that touches `manifest.yaml`.
