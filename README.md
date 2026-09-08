# AskJamie FoundRy

> The R&D forge of AskJamie™ — where reasoning models, conversation flows,
> personal knowledge systems, BrandGuard frameworks, and assistant behaviors
> are shaped and tempered.

---

## Run the workbench

```bash
python3 -m pip install -r requirements.txt
python3 -m workbench --port 8765
```

Open **http://127.0.0.1:8765**. Python 3.11 or newer is required. No frontend
build, provider key, or paid inference service is needed. Private drafts persist
in ignored `.foundry-data/`. See [the operating guide](docs/workbench.md).

Create a capability, define its behavior, add a decision flow or workflow,
record evaluations, and download a validated package. Decision exports include
a standalone offline runner. Assistant exports are editable instructions and
specifications for deployment through a separately chosen platform.

The [seven-element research](docs/research/2026-09-07-universe/universe-research.md)
explains the universe boundaries and current evidence gaps. Skillz is shared;
the three regional Found-Rys have distinct responsibilities and learn from one
another, with OverKill Found-Ry as the mentor pattern. See the
[current-state and maturation assessment](docs/current-state-and-maturation.md).

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
| **This FoundRy (public source, private local drafts)** | **[OKHP3/AskJamie-FoundRy](https://github.com/OKHP3/AskJamie-FoundRy)** |
| **This Replit Project** | **[replit.com/t/askjamie/repls/AskJamie-FoundRy](https://replit.com/t/askjamie/repls/AskJamie-FoundRy)** |
| Parent Universe | [overkillhill.com/universe](https://overkillhill.com/universe/) |
| Mentor pattern and relay lineage | [OKHP3/OverKill-Hill-FoundRy](https://github.com/OKHP3/OverKill-Hill-FoundRy) |

---

## What This Repository Is

**AskJamie FoundRy** is a private capability-building application and governance
relay. Author assistants, decision tools and guided workflows; save revisions,
record evidence, and export governed child-repository packages.

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

### Capability Registry

Capability repositories are represented in [`registry/index.yaml`](registry/index.yaml).
Earlier staged capability files and legacy folders were removed from this checkout
on 2026-07-27. The registry remains a governance record and does not prove that a
remote repository exists or is operational.

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
