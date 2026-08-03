# ADR-0002: AGENTS.md as Primary AI Context File

## Status

Accepted

## Context

AI coding assistants (Replit Agent, Cursor, Claude Code, GitHub Copilot, etc.) each
define their own convention for a root-level context file that tells the agent how
to behave in a repository. At the time this decision was made, two competing
standards existed in this repo:

- `AGENTS.md` — the OpenAI Codex / Replit Agent convention
- `CLAUDE.md` — the Anthropic Claude Code convention

Both files existed simultaneously, with different content. `AGENTS.md` was
comprehensive (10 governance sections, 3,553 bytes). `CLAUDE.md` was a thin
quick-context file (1,199 bytes) with unique entries (style rules, workspace paths,
Notion anchor) not in `AGENTS.md`.

## Decision Drivers

- **Must**: Single root-level AI context file to eliminate sync drift
- **Must**: Preserve all unique, non-redundant content from both files
- **Should**: Choose the name most broadly recognized across agent tooling
- **Should**: Avoid creating a maintenance burden from two files

## Considered Options

### Option 1: Keep AGENTS.md, merge CLAUDE.md into it (chosen)

- **Pros**: `AGENTS.md` is the richer, more authoritative document; used by Replit
  Agent (primary environment); merging preserves all CLAUDE.md content
- **Cons**: Claude Code users must read `AGENTS.md` (minor friction)

### Option 2: Keep CLAUDE.md, merge AGENTS.md into it

- **Pros**: Follows Anthropic naming convention
- **Cons**: `AGENTS.md` is the correct name for Replit Agent and OpenAI Codex;
  `AGENTS.md` has substantially more content

### Option 3: Keep both files in sync

- **Pros**: Each agent gets its preferred filename
- **Cons**: Guaranteed to drift; two sources of truth is no source of truth

## Decision

Use **`AGENTS.md`** as the single AI context file. Merge all unique content from
`CLAUDE.md` (style rules §11, project context §12) into `AGENTS.md`. Delete `CLAUDE.md`.

## Rationale

`AGENTS.md` is the primary convention for both Replit Agent (the active development
environment) and OpenAI Codex. The file already contained 10 comprehensive sections.
All CLAUDE.md-unique content (P3 brand/style rules, workspace paths, Notion anchor,
related repos) was worth preserving and fit naturally as two new sections.

## Consequences

### Positive

- Single source of truth; no sync burden
- All AI agents that look for `AGENTS.md` get the full governance picture
- Writing/style rules (§11) and project context (§12) are now part of the canonical
  governance document

### Negative

- Claude Code's convention of looking for `CLAUDE.md` first is not served; it will
  fall back to `AGENTS.md` automatically (both tools support this fallback)

### Risks

- Low: Major AI tools all support `AGENTS.md` as a recognized fallback

## Related Decisions

- [ADR-0001](0001-relay-repository-pattern.md) — overall relay structure that
  necessitates a strong AI context file

## References

- [`AGENTS.md`](../../AGENTS.md) — the current canonical file
- Replit Agent documentation — `AGENTS.md` convention
