# Synthetic pilot: assistant package

Assessment date: 2026-09-08. This pilot is synthetic and review-only.

## Package kind

`assistant`

## Goal

Define a small AskJamie assistant package that can be exported, reviewed, and
used as a private draft without implying hosted deployment.

## Pilot shape

- Title: onboarding triage assistant
- Audience: a maintainer who needs a short, bounded next step
- Purpose: turn a narrow intake into a drafted reply, checklist, or handoff
- Source boundary: synthetic prompts only, no private child or client text
- Output contract: one concise recommendation with explicit uncertainty

## Required contents

- `manifest.yaml` with private visibility and no graduation claim
- `origin/source.md` that states the pilot is synthetic
- `skill/instructions.md` with bounded drafting behavior
- `prompts/system.md` that keeps the package manual and local
- `tests/evals.json` with at least one required and one forbidden phrase check

## Validation

- Package kind stays `assistant`.
- The package remains private.
- The evaluation cases do not require model execution.
- The wording never claims an operational assistant or public repository.
- The spec can be exported without introducing client or draft leakage.

## Exit check

This pilot is ready when the package reads like a useful local draft and still
looks clearly synthetic to a reviewer.
