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

## Repository Structure

```text
.github/              GitHub automation: workflows, issue templates, PR template
_template/            Starter scaffold for new child repositories
registry/             Child repo catalog and triage log
  └── index.yaml      Master registry of all governed repos
schemas/              YAML schema definitions for manifests and registry
  ├── manifest.schema.yaml
  └── registry.schema.yaml
docs/                 Relay design, governance, naming, and migration guides
archive/              Legacy content and pre-refactor artifacts
assets/               Shared brand assets (logo, standards, identity)
  └── brand/
scripts/              Governance utility scripts (Python 3, no dependencies)
AGENTS.md             Authority chain, relay rules, and agent behavior contract
CHANGELOG.md          Version history of this FoundRy
LICENSE.md            Proprietary license
manifest.yaml         Self-describing manifest for this FoundRy
README.md             This file
```

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
