# Custom GPT Builder Skill Manifest

## Package

- **Skill name:** `custom-gpt-builder`
- **Purpose:** Build, audit, improve, package, and govern OpenAI Custom GPTs as productized AI assistants.
- **Version:** `1.0.1`
- **License decision:** Apache-2.0 is selected for this public, reusable Agent Skill infrastructure unless the owner explicitly changes the licensing posture.
- **Last verified:** 2026-06-03

## Current-platform verification rule

Platform details change frequently. Before stating limits, feature availability, pricing, model behavior, GPT Builder constraints, Actions/App compatibility, Gemini Gem capabilities, or Copilot agent behavior as definitive, verify against current official documentation or clearly label the statement as unverified.

## File inventory

| Path | Purpose | Authority |
|---|---|---:|
| `SKILL.md` | Main activation metadata, lifecycle workflow, audit checklist, and file map | Primary |
| `MANIFEST.md` | This package inventory and governance map | Primary |
| `references/repo-overlay.md` | Repository-specific brand and output alignment | Primary |
| `references/instruction-architecture.md` | 8-layer instruction architecture, No-Contradictions Rule, anti-patterns, self-check | High |
| `references/knowledge-engineering.md` | Knowledge-file preparation, retrieval behavior, manifest strategy, testing | High |
| `references/actions-and-apps.md` | Actions, Apps/connectors, OpenAPI, auth, privacy, and verification guidance | High |
| `references/platform-comparison.md` | Custom GPT vs Gemini Gem vs Copilot declarative agent comparison | Medium; verify current platform facts |
| `references/quality-tiers.md` | Poor/acceptable/good/exemplary rubric and triage model | High |
| `references/taxonomy.md` | Mapping across GPTs, Projects, chats, prompts, RAG, MCP, agents, skills, etc. | Medium |
| `references/eval-and-redteam.md` | Test prompt strategy, adversarial cases, and test logging | High |
| `evals/evals.json` | Assertion-graded eval cases for regression testing | High |

## Governance notes

1. Keep `SKILL.md` concise and task-oriented. Move long detail into `references/`.
2. Do not hard-code volatile platform claims without a verification note.
3. Keep repo-specific concerns in `references/repo-overlay.md`, not in the shared core logic.
4. Preserve the `name: custom-gpt-builder` metadata and folder-name match.
5. Update `version` when behavioral logic changes.
6. Update `last-verified` when official platform documentation is checked.
7. Do not store API keys, credentials, customer data, private GPT instructions, or proprietary source files in this skill package.
8. Treat eval failures as regressions until intentionally accepted.

## Recommended maintenance cadence

- **Monthly:** verify official GPT Builder, Actions, Apps/connectors, Gemini Gems, and Copilot agent constraints.
- **Per release:** run evals and red-team prompts.
- **Per repo fork/copy:** update `references/repo-overlay.md`.
- **Per major model/platform change:** retest knowledge retrieval, tool selection, and refusal behavior.
