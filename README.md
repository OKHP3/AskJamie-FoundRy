# AskJamie FoundRy

> The R&D forge of AskJamie™ — where reasoning models, conversation flows,
> personal knowledge systems, BrandGuard frameworks, and assistant behaviors
> are shaped and tempered.

---

## Ecosystem Position

```text
OKHP3/OverKill-Hill          ← Universe governance
  └── OKHP3/AskJamie-FoundRy ← This repository (relay FoundRy)
        ├── askjamie-aj##-*   ← Core capability repos
        ├── askjamie-brg##-*  ← BrandGuard repos
        └── [client]-askjamie-*  ← Client overlay repos
```

| Layer | URL / Repo |
|---|---|
| Storefront / Portfolio | [askjamie.bot](https://askjamie.bot/) |
| Public Portfolio Repo | [OKHP3/AskJamie](https://github.com/OKHP3/AskJamie) |
| Public Portfolio Project | [replit.com/t/askjamie/repls/AskJamie](https://replit.com/t/askjamie/repls/AskJamie) |
| **This FoundRy (private workbench)** | **[OKHP3/AskJamie-FoundRy](https://github.com/OKHP3/AskJamie-FoundRy)** |
| **This Replit Project** | **[replit.com/t/askjamie/repls/AskJamie-FoundRy](https://replit.com/t/askjamie/repls/AskJamie-FoundRy)** |
| Parent Universe | [overkillhill.com/universe](https://overkillhill.com/universe/) |
| Parent FoundRy | [OKHP3/OverKill-Hill-FoundRy](https://github.com/OKHP3/OverKill-Hill-FoundRy) |

---

## What This Repository Is

**AskJamie FoundRy** is a private R&D and governance relay. It is not a
deployable application — it is a knowledge-and-governance fabrication line
for AskJamie™ capabilities and their child repositories.

The durable asset is the **capability and knowledge architecture**. A Custom
GPT, Copilot agent, Gemini Gem, website page, or local agent is only a
*deployment surface*.

---

## Repository Catalog

Every folder has its own README. Click any link to jump to the full documentation
for that area.

### Governance and Infrastructure

| Folder | What It Is | Docs |
|---|---|---|
| [`_template/`](_template/) | Canonical starter scaffold — copy this to create any new AskJamie child repo | [ABOUT.md](_template/ABOUT.md) |
| [`registry/`](registry/) | Authoritative catalog of all 9 governed child repos plus the triage intake log | [README.md](registry/README.md) |
| [`schemas/`](schemas/) | YAML schemas for `manifest.yaml` and `registry/index.yaml` validation | [README.md](schemas/README.md) |
| [`docs/`](docs/) | Relay design, governance reference, naming conventions, migration guide, ecosystem map | [README.md](docs/README.md) |
| [`scripts/`](scripts/) | Python utilities: manifest validator, registry health check, filename normalizer | [README.md](scripts/README.md) |
| [`assets/`](assets/) | Shared AskJamie™ brand standards and identity assets | [README.md](assets/README.md) |

### Capability Efforts Staged for Graduation

Content here is ready to graduate into its own standalone repository — it is not
abandoned, just awaiting the scaffolding step.

| Folder | Capability | Code | Target Repo | Docs |
|---|---|---|---|---|
| [`archive/aj01-resume-representative/`](archive/aj01-resume-representative/) | Résumé Representative — HR, career, résumé hybridization | `aj01` | `askjamie-aj01-resume-representative` | [README.md](archive/aj01-resume-representative/README.md) |
| [`archive/brg00-builders-firstsource/`](archive/brg00-builders-firstsource/) | BrandGuard — Builders FirstSource · 🔒 BFS Firewall | `brg00` | `askjamie-brg00-builders-firstsource` | [README.md](archive/brg00-builders-firstsource/README.md) |

→ See [`archive/`](archive/README.md) for the full archive overview and graduation checklist.

### Legacy Folders

These root-level folders predate the current governance structure. Their content
has been mirrored into `archive/` (the canonical location) and is preserved here
for historical continuity pending a future consolidation pass.

| Folder | Original Name | Canonical Location | Docs |
|---|---|---|---|
| [`gpt-aj01-askjamie-resume-representative/`](gpt-aj01-askjamie-resume-representative/) | `gpt-aj01-askjamie™-—-résumé-representative/` | [`archive/aj01-resume-representative/`](archive/aj01-resume-representative/) | [README.md](gpt-aj01-askjamie-resume-representative/README.md) |
| [`okhp3-brandguard-sentinel/`](okhp3-brandguard-sentinel/) | `OKHP3-BrandGaurd-Sentinel/` | [`archive/brg00-builders-firstsource/`](archive/brg00-builders-firstsource/) | [README.md](okhp3-brandguard-sentinel/README.md) |

### Root Files

| File | Purpose |
|---|---|
| `AGENTS.md` | Authority chain, relay rules, and AI agent behavior contract |
| `manifest.yaml` | Self-describing manifest for this FoundRy relay |
| `CHANGELOG.md` | Version history in Keep a Changelog format |
| `LICENSE.md` | Proprietary license declaration |
| `README.md` | This file |

---

## Capability Families

| Code | Family | Description |
|---|---|---|
| `aj01` | Résumé Representative | Career, HR, resume hybridization |
| `aj02` | Professional Portfolio | Public-facing work portfolio |
| `aj03` | Enterprise Sleuth | Org intelligence and research |
| `aj04` | BrandGuard | Brand governance and identity protection |
| `brg##` | BrandGuard Sentinel | Client-specific brand overlays |

---

## Known Child Repositories

See [`registry/index.yaml`](registry/index.yaml) for the authoritative,
up-to-date registry of all governed child repositories.

---

## Relay Responsibilities

- Maintain AskJamie child repository scaffolds in `_template/`
- Maintain the child repo registry in `registry/index.yaml`
- Maintain manifest and registry schemas in `schemas/`
- Publish governance guidance for AskJamie, BrandGuard, and client-overlay repos
- Preserve lineage between core skills and organization-specific variants

---

## Working in This Repository

### Creating a New Child Repository

1. Copy `_template/` contents into the new repo.
2. Fill in `manifest.yaml` with correct lineage, naming, and visibility fields.
3. Add an entry to `registry/index.yaml`.
4. Follow naming conventions in `docs/naming-conventions.md`.

### Validating Manifests

```bash
python3 scripts/validate-manifest.py path/to/manifest.yaml
```

### Checking Registry Health

```bash
python3 scripts/check-registry.py
```

---

## Governance

This relay is governed by the authority chain:

```
OKHP3/OverKill-Hill → OKHP3/AskJamie-FoundRy → Child repositories
```

All agents, contributors, and automation working in this repository must
follow the rules in [`AGENTS.md`](AGENTS.md).

---

## Related

- [AskJamie™ Storefront](https://askjamie.bot/)
- [OKHP3 Universe](https://overkillhill.com/universe/)
- [OverKill Hill FoundRy](https://github.com/OKHP3/OverKill-Hill-FoundRy)
