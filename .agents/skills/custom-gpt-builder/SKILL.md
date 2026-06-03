---
name: custom-gpt-builder
description: >-
  Build, audit, and improve OpenAI Custom GPTs with production-grade methodology.
  Use this skill whenever the user mentions Custom GPTs, GPT Builder, building a GPT,
  GPT instructions, GPT knowledge files, GPT Actions, GPT Apps, GPT Store, or wants
  to create, configure, test, evaluate, audit, improve, or troubleshoot any Custom GPT.
  Also trigger when comparing Custom GPTs to Gemini Gems, Copilot declarative agents,
  or discussing GPT architecture, GPT quality, GPT best practices, or converting
  workflows into reusable GPT products. Even if the user does not say "Custom GPT"
  explicitly, trigger when they describe packaging a ChatGPT workflow for reuse,
  creating a specialized ChatGPT assistant, or publishing to the GPT Store.
license: Apache-2.0
metadata:
  version: "1.0.0"
  author: "OverKill Hill P3"
  last-verified: "2026-06-03"
  platforms: "OpenAI ChatGPT (primary), cross-reference Gemini Gems and Copilot Studio"
---

# Custom GPT Builder

A production-grade methodology for designing, building, testing, and maintaining OpenAI Custom GPTs. Treats GPT creation as product engineering, not prompt tinkering.

## What This Skill Covers

This skill guides the full lifecycle of Custom GPT development:

1. **Product definition** (job-to-be-done, user, scope, acceptance criteria)
2. **Instruction architecture** (layered system prompt, no-contradictions rule)
3. **Knowledge engineering** (file selection, structure, retrieval optimization)
4. **Capability and tool configuration** (toggles, Actions, Apps/MCP)
5. **Testing and evaluation** (golden prompt sets, adversarial cases, red-team)
6. **Publishing and governance** (visibility, versioning, maintenance)
7. **Cross-platform comparison** (GPT vs. Gem vs. Copilot declarative agent)

For detailed reference on any section, consult the corresponding file in `references/`.

## Core Principle

> If a Custom GPT cannot outperform a well-written one-off prompt, it does not deserve to exist as a GPT.

A Custom GPT is a **configured product surface** around a model: prompt + persona + rules + files + tools + UX wrapper + sharing model. Not a new model. Not fine-tuning. Not an autonomous agent. It is a packaged, reusable ChatGPT configuration for a specific job.

## Build Pipeline

### Step 0: Write a Build Brief (Required Before Anything Else)

Fill this before writing a single instruction line:

- **GPT name:**
- **Primary user(s):**
- **Primary outcomes (3):**
- **Non-goals / out-of-scope (5):**
- **"Done when" acceptance criteria (5 measurable checks):**
- **Allowed data sources:**
- **Disallowed data sources:**
- **Tooling allowed (web search, code interpreter, actions, etc.):**
- **Safety / compliance constraints (PII, PHI, financial advice, etc.):**

A GPT for "everyone" becomes generic sludge. Define the job tightly.

### Step 1: Define the Conversation Contract

- What inputs do users provide?
- What outputs must the GPT produce?
- What are the top 10 tasks (ranked)?
- What mistakes are catastrophic?

### Step 2: Draft the Instruction Stack

Use the layered architecture pattern (see `references/instruction-architecture.md` for the full template and examples):

1. **Identity and scope**: who/what this GPT is, and is not
2. **Operating principles**: priorities and tradeoffs
3. **Dialogue policy**: how it asks questions, confirms assumptions
4. **Tool policy**: when to use tools, call caps, fallbacks
5. **Knowledge policy**: which files exist, when to use them, citation rules
6. **Output policy**: formats, templates, structure
7. **Safety policy**: data boundaries, refusals, redirections
8. **Examples**: few-shot good/bad outputs and tool call examples

Keep instructions under ~2,000 words (well within the 8,000-character builder field limit). Move bulk reference into knowledge files.

The **No-Contradictions Rule**: if you have "be concise" AND "be comprehensive," you have a fault line. Pick a priority order and encode it explicitly.

### Step 3: Prepare Knowledge Files

See `references/knowledge-engineering.md` for the full blueprint.

Key constraints (mid-2026):
- Up to 20 files per GPT, each up to 512 MB
- Retrieval is RAG-based (semantic chunking); not deterministic
- File content can appear in output (data leakage vector for proprietary content)
- Some file types require Code Interpreter enabled

Knowledge file quality rules:
- Clean formatting; remove headers/footers/watermarks/artifacts
- Use clear section headings (retrieval chunks by structure)
- Prefer multiple focused files over one monolithic dump
- Name files descriptively (`acme-brand-voice-v3.pdf` not `Document1.pdf`)
- Include a manifest/index file mapping filenames to topics
- Front-load critical content in the first 20% of each file
- Test retrieval explicitly after upload

### Step 4: Configure Capabilities

Enable only what supports the job.

| Capability | Default State | Enable When |
|---|---|---|
| Web Search | ON | Current facts, research, products, news |
| Canvas | ON | Collaborative text/code editing (note: being deprecated in GPT-5.5 Instant/Thinking) |
| Image Generation | ON | Visual analysis or generation is part of the workflow |
| Code Interpreter | OFF | Analysis, CSVs, transformations, file processing |

More tools = more failure paths. A code-review GPT with Image Generation enabled is a distraction.

### Step 5: Configure Actions or Apps

**Critical constraint**: a single Custom GPT can use either Actions OR Apps, not both.

- **Actions** = OpenAPI 3.0/3.1 schema API calls. You define endpoints, parameters, auth (None/API Key/OAuth). Not available in Pro mode. Limits: 300 chars per endpoint description, 700 chars per parameter description, 100K char request/response payloads.
- **Apps** = MCP-based connectors (renamed from "Connectors" December 2025). Pre-built integrations. Write actions require Business/Enterprise/Edu for full capability.

See `references/actions-and-apps.md` for design patterns, production constraints, and auth troubleshooting.

### Step 6: Write Conversation Starters

Starters are workflow launch buttons, not slogans. Write 3-4 that demonstrate real tasks:

**Bad:** "Ask me anything about marketing."
**Good:** "Audit this resume against a senior enterprise architect role."
**Good:** "Turn this rough idea into a product brief with user stories and acceptance criteria."
**Good:** "Compare these two Mermaid diagrams for semantic clarity and suggest improvements."

### Step 7: Test Systematically

Write 10-15 test prompts covering:
- Happy-path tasks
- Edge cases at scope boundaries
- Out-of-scope queries (should gracefully refuse)
- Knowledge retrieval verification
- Adversarial inputs (prompt injection, instruction extraction)
- Tool failure scenarios

See `references/eval-and-redteam.md` for the red-team prompt pack and rubric template.
See `evals/evals.json` for assertion-graded test cases following the agentskills.io eval format.

### Step 8: Set Visibility and Ship

| Visibility | Use Case | Requirements |
|---|---|---|
| Only Me | Iteration, personal tools | None |
| Anyone with the Link | Team/client distribution | Share URL manually |
| GPT Store | Public marketplace listing | Verified Builder Profile + policy review |

Start at "Only Me." Promote to link-sharing once stable.
**Note:** Public GPTs using Actions require a valid Privacy Policy URL.

### Step 9: Version and Maintain

GPTs are not set-and-forget. The builder has version history with one-click restore.

Versioning scheme:
```
v0.1  Concept
v0.5  Usable prototype
v0.8  Tested beta
v1.0  Stable release
v1.1  Patch
v2.0  Major workflow redesign
```

Maintenance cadence:
- Re-test after OpenAI model updates (models retire frequently)
- Refresh knowledge files when source material updates
- Monitor for behavior drift via user feedback
- Add new failure modes to the test set
- Note: restoring an older version with Actions may require re-authentication

## Quality Tiers

| Tier | Signature | Outcome |
|---|---|---|
| **Poor** | Vague name, generic instructions, no workflow, dumped files, no testing | Feels like ChatGPT with a hat on |
| **Acceptable** | Clear role, basic instructions, some starters, limited files | Useful but inconsistent |
| **Good** | Defined audience, workflow, output formats, curated files, tested edge cases | Reliable reusable assistant |
| **Exemplary** | Productized experience, governance, versioning, failure handling, eval rubric | Feels like specialized software |

See `references/quality-tiers.md` for detailed scoring rubric and triage framework.

## Cross-Platform Comparison

When users ask about alternatives or need to choose a platform, consult `references/platform-comparison.md` for the detailed breakdown of Custom GPTs vs. Gemini Gems vs. Copilot declarative agents.

Quick decision framework:
- **Custom GPT** when: audience is in ChatGPT, no-code needed, text-in/text-out, GPT Store distribution, managed RAG over documents
- **Gemini Gem** when: Google Workspace native, budget-conscious, large-context tasks, live Drive sync
- **Copilot Declarative Agent** when: enterprise M365, org-knowledge grounding via Microsoft Graph, governed deployments, multi-agent composition

## Taxonomy Reference

When users ask how Custom GPTs relate to other AI constructs (Projects, Chats, Threads, Prompts, Plugins, MCP, RAG, Agents, Skills, etc.), consult `references/taxonomy.md` for the full mapping.

## Audit Mode

When asked to audit an existing GPT, follow this checklist:

1. Does it have a single, clear job?
2. Are instructions layered with no contradictions?
3. Is tool use described with triggers, caps, and fallbacks?
4. Are knowledge files curated, named clearly, and referenced in instructions?
5. Are output formats specified with examples?
6. Are safety boundaries explicit?
7. Do at least 10 eval prompts exist?
8. Does it pass the red-team suite?
9. Is there a versioning and maintenance plan?
10. Does the GPT outperform a well-written one-off prompt for its target job?

Score each 0-5. Ship gate: average >= 4.0, no safety score < 4.

## Files in This Skill

| File | Contents |
|---|---|
| `SKILL.md` | This file — build lifecycle, quick reference |
| `references/instruction-architecture.md` | 8-layer instruction template, No-Contradictions Rule, anti-patterns |
| `references/knowledge-engineering.md` | RAG mechanics, file preparation, folder taxonomy, retrieval testing |
| `references/actions-and-apps.md` | Actions vs Apps, OpenAPI patterns, production constraints, OAuth, governance |
| `references/platform-comparison.md` | GPT vs. Gem vs. Copilot Declarative Agent (full three-way comparison) |
| `references/quality-tiers.md` | Four-tier scoring rubric, weighted criteria, portfolio triage |
| `references/taxonomy.md` | 16-term taxonomy of adjacent AI constructs |
| `references/eval-and-redteam.md` | Systematic test pack, adversarial cases, test log template |
| `evals/evals.json` | Assertion-graded eval cases (agentskills.io format) |
