---
name: find-skills
description: Helps agents discover, evaluate, and recommend installable agent skills when a task may be better handled by a specialized skill. Use when users ask how to do a specialized task, whether a skill exists, or how to extend agent capabilities.
enabled: true
---

# Find Skills

Use this skill when a user asks whether an agent skill exists for a task, wants to extend the repository with reusable capabilities, or needs help choosing between existing skills and custom FoundRy-local skills.

## AskJamie Context

Prefer skills that support conversation design, BrandGuard governance, RAG/knowledge architecture, assistant behavior, documentation, evaluation, and safe deployment variants.

## Process

1. Identify the user intent and domain.
2. Check whether the task should use an external installable skill, a local `.agents/skills/` skill, or a new AskJamie capability repo.
3. Prefer reputable sources and official skill packages when recommending external skills.
4. For AskJamie work, consider whether the capability should become a reusable BrandGuard, Enterprise Sleuth, or assistant-behavior child repo.

## Output

Return the recommended skill or skill family, the reason, install/copy guidance, and whether the capability should become a local skill or child repository.
