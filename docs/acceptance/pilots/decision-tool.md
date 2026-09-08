# Synthetic pilot: decision-tool package

Assessment date: 2026-09-08. This pilot is synthetic and review-only.

## Package kind

`decision-tool`

## Goal

Define a small decision package that exercises branching logic, exportability,
and deterministic evaluation without relying on arbitrary code.

## Pilot shape

- Title: governed launch gate
- Audience: a maintainer deciding whether a capability is ready for the next step
- Purpose: route a narrow yes/no intake to a reviewed result and a next action
- Source boundary: synthetic decision graph and synthetic cases only
- Output contract: one terminal result per branch, plus a clear follow-up path

## Required contents

- `manifest.yaml` with private visibility and no graduation claim
- `origin/source.md` that states the graph is synthetic
- `skill/instructions.md` that names the question, yes branch, and no branch
- `decision/graph.json` or equivalent graph data with a single start node
- `tests/evals.json` with cases for the yes path, no path, and a terminal check

## Validation

- Package kind stays `decision-tool`.
- Every question has both `yes` and `no` paths.
- Every branch ends in a result node.
- The graph has no dangling nodes or unreachable answers.
- The exported runner stays offline and script-safe.

## Exit check

This pilot is ready when the decision path is obvious to a reviewer and the
graph still feels intentionally small.
