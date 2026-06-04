# AGENTS.md — [REPO_NAME]

> **Template instruction:** Replace every `[PLACEHOLDER]` before using this file.
> Delete this notice block when the repo is live.

---

## 0. Role

This repository is a **[TYPE]** within the AskJamie™ ecosystem, governed by
the relay at `OKHP3/AskJamie-FoundRy`.

Replace `[TYPE]` with one of: `core capability`, `BrandGuard sentinel`,
`enterprise-sleuth variant`, `client overlay`, `conversation-design system`,
`RAG experiment`.

---

## 1. Authority Chain

```text
OKHP3/OverKill-Hill
  → OKHP3/AskJamie-FoundRy
    → [REPO_NAME]  ← This repository
```

---

## 2. Repository Purpose

[Describe what this repo does in 2–4 sentences. What capability does it
encapsulate? What deployment surfaces does it support?]

---

## 3. Lineage

- **Parent FoundRy:** `OKHP3/AskJamie-FoundRy`
- **Capability code:** `[aj## | brg## | custom]`
- **Capability slug:** `[capability-slug]`
- **Full name:** `askjamie-[code]-[slug]`

---

## 4. Directory Contract

```text
docs/       Design notes, research, governance docs for this capability
origin/     Source prompts and raw instruction text (pre-refinement)
skill/      Refined, deployable prompt and skill artifacts
prompts/    Versioned prompt files ready for deployment surfaces
research/   Supporting research, competitive analysis, references
tests/      Evaluation prompts, expected outputs, regression checks
schemas/    Local YAML/JSON schemas specific to this repo
assets/     Logos, images, brand assets used by this capability
exports/    Deployment exports (GPT config JSON, Copilot YAML, etc.)
archive/    Retired versions, deprecated content
```

---

## 5. Required Files

This repository must always maintain:

- `AGENTS.md` — this file
- `README.md` — capability overview and usage guide
- `CHANGELOG.md` — version history
- `LICENSE.md` — license declaration
- `manifest.yaml` — lineage, visibility, and governance metadata

---

## 6. Agent Behavior

AI agents working in this repository must:

- Preserve parent-child lineage declared in `manifest.yaml`.
- Never commingle client-sensitive content with public portfolio artifacts.
- Update `manifest.yaml` when the status, visibility, or scope changes.
- Treat any content labeled `bfs_firewall` or `visibility_lock: permanent-private`
  as confidential and not for public sharing or summarization.
- Refer to `OKHP3/AskJamie-FoundRy` relay for naming, schema, and governance
  guidance.

---

## 7. Deployment Surfaces

This capability can be deployed to:

- [ ] OpenAI Custom GPT
- [ ] Microsoft Copilot Studio
- [ ] Google Gemini Gem
- [ ] Replit Agent
- [ ] Website / API integration
- [ ] Other: [specify]

---

## 8. Canonical Principle

The durable asset is the capability and knowledge architecture stored in this
repository. Any platform or deployment surface is ephemeral by comparison.
