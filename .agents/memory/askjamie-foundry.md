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

## Historical content
- AJ01, BRG00, and their former archive and legacy folders were removed from
  this checkout on 2026-07-27.
- Their registry identities remain as governance records. Do not recreate local
  source copies without an explicit source, owner, and recovery plan.

## BFS firewall
Repos with `bfs_firewall: true` (brg00, buildersfirstsource client overlay) are permanently private. Never summarize or share content publicly.
