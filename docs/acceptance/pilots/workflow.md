# Synthetic pilot: workflow package

Assessment date: 2026-09-08. This pilot is synthetic and review-only.

## Package kind

`workflow`

## Goal

Define a small workflow package that demonstrates ordered steps, durable
instructions, and a checklist-style export with no external side effects.

## Pilot shape

- Title: controlled refresh checklist
- Audience: a maintainer preparing a governed update
- Purpose: show a step-by-step sequence for a reviewable maintenance action
- Source boundary: synthetic steps only, no private source content
- Output contract: one ordered checklist with explicit finish criteria

## Required contents

- `manifest.yaml` with private visibility and no graduation claim
- `origin/source.md` that states the workflow is synthetic
- `skill/instructions.md` with ordered steps and stop points
- `prompts/system.md` that keeps the package local and manual
- `workflow/steps.md` or equivalent step list with clear ordering

## Validation

- Package kind stays `workflow`.
- The steps are ordered and self-contained.
- No step implies an automatic external action.
- The package can be exported as a checklist, not executed as a service.
- The wording stays free of client or draft content.

## Exit check

This pilot is ready when the checklist is easy to follow and impossible to
mistake for automation.
