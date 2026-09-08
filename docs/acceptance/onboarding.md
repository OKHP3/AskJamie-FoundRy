# Onboarding and description audit

Assessment date: 2026-09-08. This is an audit guide, not a product claim.

## Purpose

Use this note when a repo-private description looks stale and needs a safe review.
The goal is to update wording from current in-repo evidence without exposing child
repo text, private drafts, or client-specific material.

## Safe boundary

Only summarize what the repository already shows.

- Keep child repo names, draft source text, and client overlay details private.
- Describe private items by class, status, and governance state, not by content.
- Do not infer that a registry entry, draft export, or local package proves a
  remote repository, hosted assistant, or public release.
- If a line would repeat protected content, replace it with a neutral placeholder
  and note the reason for withholding.

## What to check

| Area | What may be stale | What to do |
|---|---|---|
| `docs/current-state-and-maturation.md` | Old PR status or old test counts | Reconcile to merged PRs and current local test evidence |
| `docs/workbench.md` | Language that sounds like hosted deployment or live model access | Keep it loopback-only, local, and deterministic |
| `docs/relay-design.md` | Wording that implies a draft export created a child repo | Keep export, proposal, and registration separate |
| `docs/governance.md` | Public-graduation or privacy language that drifts from the schema | Preserve permanent-private controls exactly |
| `workbench/data/skills.json` | Snapshot age, counts, or descriptions that have drifted from the source catalog | Treat it as a dated reference, not runtime truth |

## Stale-description patterns

- "awaiting merge" after the PR is already on main.
- "latest" or "current" without a date or retrieval note.
- Descriptions that present selected Skillz metadata as validated runtime behavior.
- Copying child or draft text into a public-facing doc instead of summarizing the
  governing rule.
- Any wording that weakens `visibility_lock: permanent-private`,
  `bfs_firewall: true`, or client overlay privacy.

## Audit output

Record three things for each reviewed line:

1. Confirmed.
2. Stale or inferred.
3. Withheld for privacy.

Keep the result short. The point is to refresh the wording, not to expand the
surface area of private detail.

## Verified results

The root manifest and AGENTS.md correctly describe public source. README.md
still called this relay a private workbench; that label is now corrected.
Private child defaults and permanent-private flags remain unchanged.
The three adjacent JSON pilots were normalized and exported on 2026-09-08;
all generated manifests passed the canonical schema and retained private visibility.
The Markdown files describe intent; JSON fixtures are executable synthetic input.
