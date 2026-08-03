# ADR-0001: Relay Repository Pattern

## Status

Accepted

## Context

The AskJamie capability ecosystem needs governance across multiple repositories:
a parent universe (`OKHP3/OverKill-Hill`), a relay layer, and individual capability
repos for each AskJamie product (e.g., AJ01 résumé assistant, BRG00 BrandGuard).

Without a relay layer, governance documents, scaffolds, schemas, and brand assets
would need to be duplicated into every child repo, and updates to shared conventions
would require touching every downstream repo.

## Decision Drivers

- **Must**: Enable canonical governance (schemas, scaffolds, naming rules) to flow
  to child repos without duplication
- **Must**: Stage capability content (GPTs, skills, prompts) before it graduates
  to an independent repo
- **Should**: Keep the relay repo itself free of deployable application code
- **Should**: Be navigable without deep knowledge of the repo structure

## Considered Options

### Option 1: Relay Repository (chosen)

A dedicated repository that sits between the parent universe and child capability
repos. It holds governance artifacts, distributes scaffolds via `_template/`, and
stages legacy/pre-graduation content in `archive/`.

- **Pros**: Single source of truth for governance; clear upgrade path; child repos
  stay focused; relay itself is lightweight and non-deployable
- **Cons**: Adds one repository to navigate; requires discipline to not accumulate
  runtime code here

### Option 2: Flat universe repository

All capabilities and governance in one monorepo under `OKHP3/OverKill-Hill`.

- **Pros**: Single repo; no relay needed
- **Cons**: Monorepo grows large; capability teams can't work independently; child
  GPT packages would sit next to governance docs with no clear boundary

### Option 3: Per-capability repos with no relay

Each capability (AJ01, BRG00, etc.) manages its own governance and scaffold.

- **Pros**: Maximum isolation
- **Cons**: Governance drift; duplicated schemas; no single place to install shared
  Agent Skills

## Decision

We will use a **relay repository** (`OKHP3/AskJamie-FoundRy`) as the governance
and scaffolding hub between the parent universe and AskJamie capability repos.

## Rationale

The relay pattern keeps deployable code out of the governance layer, provides a
natural staging area for capability content before it earns its own repo, and
ensures that schemas and scaffolds have a single authoritative home.

## Consequences

### Positive

- Governance updates propagate cleanly from relay to child repos
- `registry/index.yaml` is the canonical map of all AskJamie capabilities
- `_template/` gives every new capability a compliant starting shape
- Agent Skills installed here are available to any project that mirrors this relay

### Negative

- Developers must navigate three layers (universe → relay → capability repo)
- Risk of accumulating non-relay content here over time (must be actively guarded)

### Risks

- If the relay grows too large, it becomes harder to navigate
- Mitigation: `docs/governance.md` documents what belongs here vs. in child repos

## Related Decisions

- [ADR-0002](0002-agents-md-as-ai-context-file.md) — how AI agents are briefed on
  this relay pattern
- [ADR-0003](0003-uppercase-skill-md-naming.md) — naming conventions for distributed
  skill files

## References

- [`docs/relay-design.md`](../relay-design.md) — relay architecture documentation
- [`registry/README.md`](../../registry/README.md) — capability registry
- [`_template/ABOUT.md`](../../_template/ABOUT.md) — child repo scaffold description
