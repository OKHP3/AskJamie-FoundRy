---
name: AskJamie FoundRy Structure
description: Governance relay layout, naming conventions, ecosystem map, and script usage for OKHP3/AskJamie-FoundRy.
---

## Role
This repo is a private R&D governance relay (not a deployable app). No workflow, no server.

## Ecosystem
- Parent: OKHP3/OverKill-Hill → OKHP3/OverKill-Hill-FoundRy
- This relay: OKHP3/AskJamie-FoundRy (Replit: AskJamie-FoundRy project)
- Public storefront: askjamie.bot / OKHP3/AskJamie / AskJamie Replit project
- Universe: overkillhill.com/universe

## Key naming patterns
- Core capabilities: `askjamie-aj##-[slug]`
- BrandGuard: `askjamie-brg##-[brand-slug]`
- Client overlays: `[org]-askjamie-[code]-[slug]` (permanent-private, never public)

## Validation scripts (require pyyaml + jsonschema)
- `python3 scripts/validate-manifest.py path/to/manifest.yaml`
- `python3 scripts/check-registry.py`
- GitHub Actions in `.github/workflows/` run these on PRs automatically.

## Important rule: foundry-relay type
The root `manifest.yaml` has `identity.type: foundry-relay` and `lineage.parent_foundry: OKHP3/OverKill-Hill`. The validate-manifest.py script has special-case logic for this type — it skips the child-repo parent_foundry check.

## Legacy content
- `gpt-aj01-askjamie™-—-résumé-representative/` — original aj01 content, copied to `archive/aj01-resume-representative/`, legacy folder still in git
- `OKHP3-BrandGaurd-Sentinel/BFS-Framing-Intelligent-Futures/` — brg00 BFS content, copied to `archive/brg00-builders-firstsource/`, legacy folder still in git
- Both legacy folders should be git rm'd in a future cleanup commit

**Why:** These folders predate the naming convention and cannot be safely deleted via agent tools (destructive git op). Archived copies exist in `archive/`.

## BFS firewall
Repos with `bfs_firewall: true` (brg00, buildersfirstsource client overlay) are permanently private. Never summarize or share content publicly.
