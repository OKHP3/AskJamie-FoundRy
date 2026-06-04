# Ecosystem Map — AskJamie™ & OKHP3 Universe

## Universe Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│  OKHP3 Universe                                                 │
│  https://overkillhill.com/universe/                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OverKill Hill FoundRy  (OKHP3/OverKill-Hill-FoundRy)   │  │
│  │  Parent governance relay for all OKHP3 domains          │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │ governs                             │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │  AskJamie FoundRy  (OKHP3/AskJamie-FoundRy)             │  │
│  │  Domain relay — this repository                          │  │
│  └──┬─────────────────────────────────────────────────┬─────┘  │
│     │ core capabilities                 BrandGuard +  │         │
│     │                                  client overlays│         │
│  ┌──▼──────────────┐              ┌────▼─────────────┐│         │
│  │ askjamie-aj01   │              │ askjamie-brg00   ││         │
│  │ askjamie-aj02   │              │ askjamie-brg01   ││         │
│  │ askjamie-aj03   │              │ ...              ││         │
│  │ askjamie-aj04   │              │ buildersfirst-   ││         │
│  └─────────────────┘              │ source-askjamie  ││         │
│                                   └──────────────────┘│         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Three-Way Pairing: Public Face ↔ Private Workbench

Each AskJamie deployment surface has a corresponding private workbench pairing:

| Layer | Public / Storefront | Private Workbench |
|---|---|---|
| **Website** | [askjamie.bot](https://askjamie.bot/) | — |
| **GitHub** | [OKHP3/AskJamie](https://github.com/OKHP3/AskJamie) | [OKHP3/AskJamie-FoundRy](https://github.com/OKHP3/AskJamie-FoundRy) |
| **Replit** | [AskJamie](https://replit.com/t/askjamie/repls/AskJamie) | [AskJamie-FoundRy](https://replit.com/t/askjamie/repls/AskJamie-FoundRy) |

The public-facing trio (`askjamie.bot` + `OKHP3/AskJamie` + Replit `AskJamie`)
is the **storefront, catalog, or portfolio** of solutions.

The private workbench trio (`AskJamie-FoundRy` repo + Replit project) is the
**R&D fabrication line** where capabilities are designed, tempered, and staged
before public exposure.

---

## OverKill Hill Parallel

The AskJamie pairing mirrors the OverKill Hill domain structure:

| Domain | FoundRy (workbench) | Portfolio (public) |
|---|---|---|
| OverKill Hill | [OKHP3/OverKill-Hill-FoundRy](https://github.com/OKHP3/OverKill-Hill-FoundRy) | [overkillhill.com](https://overkillhill.com/) |
| AskJamie™ | [OKHP3/AskJamie-FoundRy](https://github.com/OKHP3/AskJamie-FoundRy) | [askjamie.bot](https://askjamie.bot/) |

---

## Capability Family Map

### Core Capabilities (`aj##`)

| Code | Name | Status | Public |
|---|---|---|---|
| `aj01` | Résumé Representative | Active | Candidate |
| `aj02` | Professional Portfolio | Draft | Candidate |
| `aj03` | Enterprise Sleuth | Draft | Candidate |
| `aj04` | BrandGuard (core) | Draft | Candidate |

### BrandGuard Sentinels (`brg##`)

| Code | Brand | Status | Public |
|---|---|---|---|
| `brg00` | Builders FirstSource | Active | Never (private) |
| `brg01` | LEGO | Planned | TBD |
| `brg12` | Mathews Archery | Planned | TBD |

### Client Overlays

| Client Org | Base Capability | Status | Public |
|---|---|---|---|
| Builders FirstSource | aj03 Enterprise Sleuth | Draft | Never |
| CVS Health | aj03 Enterprise Sleuth | Draft | Never |

---

## Data Flow: Fabrication to Deployment

```text
AskJamie FoundRy (private)
  │
  ├── Ideation & R&D
  │     └── origin/  (raw prompts, research)
  │
  ├── Refinement
  │     └── skill/   (tempered capability artifacts)
  │
  ├── Staging
  │     └── prompts/ (versioned, deployment-ready)
  │
  └── Export
        └── exports/ (GPT JSON, Copilot YAML, etc.)
              │
              ▼
        Deployment Surfaces
              ├── OpenAI Custom GPT
              ├── Microsoft Copilot
              ├── Google Gemini Gem
              └── Replit Agent / API
                    │
                    ▼
              Public Portfolio
                    ├── askjamie.bot
                    └── OKHP3/AskJamie (GitHub)
```

---

## Governance Data Flow

```text
OKHP3/OverKill-Hill
  │  (golden standards, universe governance)
  ▼
OKHP3/AskJamie-FoundRy
  │  (domain relay: translates + distributes)
  ├── _template/       → new child repos inherit scaffold
  ├── schemas/         → child repos validate manifests against
  ├── docs/            → child repos reference for governance
  └── registry/        → authoritative catalog of all children
        │
        ▼
  Child Repositories   → govern their own content within relay rules
```
