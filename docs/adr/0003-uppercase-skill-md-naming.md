# ADR-0003: UPPERCASE SKILL.md and README.md Naming Convention

## Status

Accepted

## Context

Agent Skill packages each contain a primary instruction file. When the skills were
first migrated into this repository under `.agents/skills/`, several arrived with
lowercase filenames (`skill.md`, `readme.md`) due to inconsistent authoring
conventions across source repositories.

The Replit environment and most Unix-based CI systems are case-sensitive. A skill
loaded as `skill.md` on a case-insensitive macOS filesystem would silently fail
on a case-sensitive Linux host if the loader expected `SKILL.md`.

## Decision Drivers

- **Must**: Consistent, case-safe naming across all platforms (macOS, Linux, Windows)
- **Must**: Match the naming convention used by Replit's native skill discovery
  (which expects `SKILL.md`)
- **Should**: Match the convention used in the OKHP3/skillz distribution repository
- **Should**: Be enforceable by a simple automated scan

## Considered Options

### Option 1: UPPERCASE (SKILL.md, README.md) — chosen

- **Pros**: Matches Replit discovery, OKHP3/skillz canonical convention, and common
  open-source conventions (README.md is the universal standard); easily audited
- **Cons**: Requires renaming files from earlier repos that used lowercase

### Option 2: Lowercase (skill.md, readme.md)

- **Pros**: Consistent with some academic and Unix-purist conventions
- **Cons**: Breaks Replit skill discovery; diverges from OKHP3/skillz; README.md
  is the GitHub-standard name

### Option 3: Allow both, rely on case-insensitive OS

- **Pros**: No renaming needed
- **Cons**: Silent failures on Linux; impossible to enforce without a linter

## Decision

All Agent Skill instruction files must be named **`SKILL.md`** (uppercase). All
documentation index files must be named **`README.md`** (uppercase). No exceptions
within `.agents/skills/`.

## Rationale

UPPERCASE is the canonical convention in Replit Agent's skill discovery, in
OKHP3/skillz, and in GitHub/open-source norms for README.md. The cost of renaming
is low (single `mv` command per file). The cost of inconsistency is silent
case-sensitive failures on Linux hosts.

## Consequences

### Positive

- Replit skill discovery reliably loads all 18 installed skills
- `find . -iname "skill.md"` scan can detect regressions
- OKHP3/skillz mirrors stay in sync without case-translation

### Negative

- Requires a one-time rename pass when installing skills from case-insensitive
  sources (macOS, Windows)

### Risks

- New skill installs from external sources may arrive with lowercase names;
  mitigated by the audit scan documented in `AGENTS.md`

## Related Decisions

- [ADR-0001](0001-relay-repository-pattern.md) — relay pattern that requires
  consistent skill delivery to child repos

## References

- [`AGENTS.md`](../../AGENTS.md) — §9 documents the skill naming rule
- [`.agents/skills/README.md`](../../.agents/skills/README.md) — skill catalog
