# AGENTS.md — AskJamie-FoundRy

## 0. Role

This repository is the AskJamie FoundRy relay. It translates golden governance from `OKHP3/OverKill-Hill` into reusable scaffolds for AskJamie child repositories, including AskJamie core capabilities, BrandGuard systems, Enterprise Sleuth variants, conversation-design assets, personal knowledge systems, and RAG-oriented assistant behavior.

## 1. Authority Chain

```text
OKHP3/OverKill-Hill
  → OKHP3/AskJamie-FoundRy
    → AskJamie child repositories
```

## 2. Relay Responsibilities

This repository owns:

- AskJamie child repository scaffolds in `_template/`
- AskJamie repo registry files in `registry/`
- Manifest and registry schemas in `schemas/`
- Relay documentation in `docs/`
- GitHub workflow templates in `.github/`
- Governance guidance for AskJamie, BrandGuard, and client-overlay repositories

## 3. Child Repository Scope

This relay governs repositories matching these families:

- `askjamie-aj##-*`
- `askjamie-brg##-*`
- `[client-org]-askjamie-*`
- AskJamie assistant, RAG, identity, and conversation repositories

Known child examples include:

- `askjamie-aj01-resume-representative`
- `askjamie-aj02-professional-portfolio`
- `askjamie-aj03-enterprise-sleuth`
- `askjamie-aj04-brandguard`
- `askjamie-brg00-builders-firstsource`
- `askjamie-brg01-lego` through `askjamie-brg12-mathews-archery`
- `buildersfirstsource-askjamie-aj03-enterprise-sleuth`
- `cvshealth-askjamie-aj03-enterprise-sleuth`

## 4. Client Overlay Rule

Client or organization overlay repos are deployment overlays, not normal public-candidate repos.

If a repo includes `client_org`, `bfs_firewall`, or `visibility_lock: permanent-private`, public graduation is blocked unless Jamie explicitly overrides the lock in writing.

## 5. Required Child Repo Files

Every governed child repo should eventually contain:

```text
AGENTS.md
README.md
CHANGELOG.md
LICENSE.md
manifest.yaml
```

Capability repos should additionally include:

```text
docs/
origin/
skill/
prompts/
research/
tests/
schemas/
assets/
exports/
archive/
```

## 6. Naming Rules

Preferred AskJamie patterns:

```text
askjamie-aj##-[capability-slug]
askjamie-brg##-[brand-slug]
[client-org]-askjamie-[capability-code]-[capability-slug]
```

## 7. Manifest Requirements

Required lineage fields:

```yaml
brand_domain: askjamie
parent_foundry: OKHP3/AskJamie-FoundRy
governance.naming_pattern: ""
```

Client overlays must additionally declare:

```yaml
lineage.parent_capability: ""
visibility_control.client_org: ""
visibility_control.visibility_lock: permanent-private
visibility_control.public_graduation_allowed: false
```

## 8. Agent Behavior

AI agents working in this repo must:

- Preserve parent-child lineage.
- Treat BrandGuard repos as public-source-only unless explicitly told otherwise.
- Treat BFS/client-org repos as sensitive and private by default.
- Update `registry/index.yaml` when child relationships are created or materially changed.
- Avoid commingling AskJamie client overlays with public portfolio artifacts.

## 9. Directory Contract

```text
_template/   Child repo starter scaffold
registry/    Child repo catalog and triage logs
schemas/     Manifest and registry validation schemas
docs/        Relay design, governance, and migration guidance
.github/     GitHub workflow and issue template scaffolds
```

## 10. Canonical Principle

AskJamie capabilities are reusable reasoning and conversation systems. A Custom GPT, Copilot agent, Gem, skill, website page, or local agent is only a deployment surface.

## 11. Writing and Style Rules

These rules apply to all AI agents and contributors generating content in this repository
or any governed child repo.

- **No em dashes** in any generated content. Use a colon, comma, or restructure the
  sentence instead.
- **Preserve standalone punchy lines.** Do not consolidate short, punchy sentences into
  surrounding paragraphs. They are intentional for rhythm and scannability.
- **ROY principle:** understanding produced / explanation invested — verbosity must earn
  its space. Prefer concise, direct prose. Do not pad or over-explain.
- **AutoCAD version is R10** — locked, not negotiable. Do not reference or suggest a
  different AutoCAD version in any content.

## 12. Project Context

Quick-reference metadata for agents and contributors.

| Field | Value |
|---|---|
| Suite | FoundRy / AskJamie |
| Type | Development Lab (R&D governance relay — not a deployable app) |
| GitHub | https://github.com/OKHP3/AskJamie-FoundRy |
| Notion Anchor | https://app.notion.com/p/2aaa7fb7da3f4338b5d7402754aee9b0 |
| Windows Local Path | `C:\Users\jamie\OKH-Local\Projects\askjamie-foundry` |
| Mac Local Path | `/Volumes/OKH-Local/04_GitHub_Mirrors/AskJamie-FoundRy` |

### Related Repositories

- [OKHP3/AskJamie](https://github.com/OKHP3/AskJamie) — public portfolio (sibling)
- [OKHP3/OverKill-Hill](https://github.com/OKHP3/OverKill-Hill) — parent universe governance
- [OKHP3/OverKill-Hill-FoundRy](https://github.com/OKHP3/OverKill-Hill-FoundRy) — parent FoundRy relay