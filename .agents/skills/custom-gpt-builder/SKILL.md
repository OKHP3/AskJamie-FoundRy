---
name: custom-gpt-builder
description: >-
  Build, audit, and improve OpenAI Custom GPTs with production-grade methodology.
  Use this skill when the user asks to create, configure, test, evaluate, audit,
  improve, troubleshoot, compare, document, or package a Custom GPT or reusable
  ChatGPT workflow. Also use it for GPT Builder instructions, knowledge files,
  Actions, Apps/connectors, GPT Store readiness, Gemini Gem comparison, Copilot
  declarative-agent comparison, or conversion between Custom GPTs and Agent Skills.
license: Apache-2.0
metadata:
  version: "1.0.1"
  author: "OverKill Hill P3"
  last-verified: "2026-06-03"
  license_decision: "Apache-2.0 selected for public, reusable Agent Skill infrastructure; revise only by explicit owner decision."
  platforms: "OpenAI ChatGPT primary; cross-reference Gemini Gems and Copilot Studio when relevant"
---

# Custom GPT Builder

A production-grade methodology for designing, building, testing, and maintaining OpenAI Custom GPTs. Treats GPT creation as product engineering, not prompt tinkering.

## Current-platform verification rule

Platform details change frequently. Before stating limits, feature availability, pricing, model behavior, GPT Builder constraints, Actions/App compatibility, Gemini Gem capabilities, or Copilot agent behavior as definitive, verify against current official documentation or clearly label the statement as unverified. Prefer stable design principles over brittle platform trivia.

## What This Skill Covers

This skill guides the full lifecycle of Custom GPT development:

1. **Product definition** (job-to-be-done, user, scope, acceptance criteria)
2. **Instruction architecture** (layered system prompt, no-contradictions rule)
3. **Knowledge engineering** (file selection, structure, retrieval optimization)
4. **Capability and tool configuration** (toggles, Actions, Apps/MCP/connectors)
5. **Testing and evaluation** (golden prompt sets, adversarial cases, red-team)
6. **Publishing and governance** (visibility, versioning, maintenance)
7. **Cross-platform comparison** (GPT vs. Gem vs. Copilot declarative agent)
8. **Repo-native packaging** (manifest, overlays, evals, references, and source-of-truth discipline)

For detailed reference on any section, consult the corresponding file in `references/` and the package map in `MANIFEST.md`.

## Core Principle

> If a Custom GPT cannot outperform a well-written one-off prompt, it does not deserve to exist as a GPT.

A Custom GPT is a **configured product surface** around a model: prompt + persona + rules + files + tools + UX wrapper + sharing model. Not a new model. Not fine-tuning. Not automatically an autonomous agent. It is a packaged, reusable ChatGPT configuration for a specific job.

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
- **Tooling allowed (web search, code interpreter/data analysis, actions, apps/connectors, etc.):**
- **Safety / compliance constraints (PII, PHI, financial advice, legal review, regulated data, etc.):**

A GPT for "everyone" becomes generic sludge. Define the job tightly.

### Step 1: Define the Conversation Contract

- What inputs do users provide?
- What outputs must the GPT produce?
- What are the top 10 tasks (ranked)?
- What mistakes are catastrophic?
- Which assumptions may be inferred, and which require clarification?

### Step 2: Draft the Instruction Stack

Use the layered architecture pattern (see `references/instruction-architecture.md` for the full template and examples):

1. **Identity and scope**: who/what this GPT is, and is not
2. **Operating principles**: priorities and tradeoffs
3. **Dialogue policy**: how it asks questions, confirms assumptions
4. **Tool policy**: when to use tools, call caps, fallbacks
5. **Knowledge policy**: which files exist, when to use them, citation rules
6. **Output policy**: formats, templates, structure
7. **Safety policy**: data boundaries, refusals, redirections
8. **Examples**: few-shot good/bad outputs and tool-call examples

Keep instructions dense. Move bulk reference into knowledge files. Use the builder’s current published limits as a constraint, but verify those limits before treating them as fixed.

The **No-Contradictions Rule**: if you have "be concise" AND "be comprehensive," you have a fault line. Pick a priority order and encode it explicitly.

### Step 3: Prepare Knowledge Files

See `references/knowledge-engineering.md` for the full blueprint.

Use current official GPT Builder documentation for hard limits. Common design constraints to verify include:

- Number of files allowed per GPT
- Maximum file size
- Supported file types
- Whether a file type requires Code Interpreter/Data Analysis
- Retrieval behavior and citation behavior

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

| Capability | Default Bias | Enable When |
|---|---|---|
| Web/search | Verify need | Current facts, research, products, news, platform checks |
| Canvas/editor surface | Verify availability | Collaborative text/code editing is part of the workflow |
| Image generation | Usually off unless needed | Visual generation is part of the workflow |
| Code Interpreter/Data Analysis | Usually off unless needed | Analysis, CSVs, transformations, file processing |
| Apps/connectors | Verify availability | Platform-native integrations are required |
| Actions | Verify availability | Custom OpenAPI-backed API calls are required |

More tools = more failure paths. A code-review GPT with Image Generation enabled is usually a distraction.

### Step 5: Configure Actions, Apps, or Connectors

Check the current GPT Builder surface before committing to an integration model. Some GPT Builder configurations require choosing between custom Actions and platform Apps/connectors. Do not promise that both can be used together until verified in current documentation or in the Builder UI.

- **Actions** = OpenAPI schema API calls. You define endpoints, parameters, auth, and side-effect behavior.
- **Apps/connectors** = platform-native or MCP-style integrations where available. Availability, write permissions, and admin controls vary by plan and workspace.

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
- Platform-constraint verification

See `references/eval-and-redteam.md` for the red-team prompt pack and rubric template. See `evals/evals.json` for assertion-graded test cases following the local Agent Skills eval format.

### Step 8: Set Visibility and Ship

| Visibility | Use Case | Requirements |
|---|---|---|
| Only Me | Iteration, personal tools | None beyond builder access |
| Anyone with the Link | Team/client distribution | Share URL manually; check workspace policy |
| GPT Store/Public | Public marketplace listing | Verify Builder Profile, policy review, and current requirements |

Start at "Only Me." Promote to link-sharing once stable. Public GPTs using external Actions commonly require a valid Privacy Policy URL; verify current requirements before publishing.

### Step 9: Version and Maintain

GPTs are not set-and-forget. Use builder version history when available and keep the repo-side source of truth current.

Versioning scheme:

```text
v0.1  Concept
v0.5  Usable prototype
v0.8  Tested beta
v1.0  Stable release
v1.1  Patch
v2.0  Major workflow redesign
```

Maintenance cadence:

- Re-test after major model or platform updates
- Refresh knowledge files when source material updates
- Monitor for behavior drift via user feedback
- Add new failure modes to the test set
- Re-check Actions/apps/connectors after platform changes or auth changes

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

- **Custom GPT** when: audience is in ChatGPT, no-code packaging is needed, GPT Store/public sharing matters, or managed document grounding is sufficient
- **Gemini Gem** when: Google Workspace-native workflows and Google context are the center of gravity; verify current Gem limits and Drive behavior before claiming specifics
- **Copilot Declarative Agent** when: enterprise M365, Microsoft Graph grounding, governed deployment, or Copilot Studio lifecycle controls are required

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
11. Are time-sensitive platform claims verified or labeled as assumptions?
12. Does the repo-specific overlay align outputs to the target repository and brand?

Score each 0-5. Ship gate: average >= 4.0, no safety/governance/platform-verification score < 4.

## Files in This Skill

| File | Contents |
|---|---|
| `SKILL.md` | This file — build lifecycle, quick reference |
| `MANIFEST.md` | Package map, governance notes, verification policy, file inventory |
| `references/repo-overlay.md` | Repository-specific brand, scope, and output alignment |
| `references/instruction-architecture.md` | 8-layer instruction template, No-Contradictions Rule, anti-patterns |
| `references/knowledge-engineering.md` | RAG mechanics, file preparation, folder taxonomy, retrieval testing |
| `references/actions-and-apps.md` | Actions vs Apps/connectors, OpenAPI patterns, production constraints, OAuth, governance |
| `references/platform-comparison.md` | GPT vs. Gem vs. Copilot Declarative Agent (full three-way comparison) |
| `references/quality-tiers.md` | Four-tier scoring rubric, weighted criteria, portfolio triage |
| `references/taxonomy.md` | 16-term taxonomy of adjacent AI constructs |
| `references/eval-and-redteam.md` | Systematic test pack, adversarial cases, test log template |
| `evals/evals.json` | Assertion-graded eval cases |
