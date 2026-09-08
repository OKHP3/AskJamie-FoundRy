# Agent collaboration protocol

One task, explicit ownership, reusable evidence.

## Scope and routing

The owner prefers lower total token expenditure over speed. As of 2026-09-07,
the owner reports more ChatGPT capacity, some Claude capacity, and limited
Copilot capacity while Replit reconciliation is already underway. This is a
planning preference, not a live quota reading. Check available access when
assigning work; do not assume subscriptions or allowances transfer between tools.

| Platform | Preferred contribution |
|---|---|
| ChatGPT/Codex | Substantial implementation, conflict analysis, integration planning, and local validation |
| Claude | Bounded independent review or an isolated implementation task when useful |
| GitHub Copilot | Small fixes, focused test assistance, and targeted review |
| Replit | Actual Replit Git reconciliation, environment checks, and workspace-specific execution |

Use shell tools and existing validators for deterministic work. Choose the
least expensive available model and reasoning effort likely to succeed. Escalate
only the difficult subproblem. After two failed attempts with the same approach,
change approach or hand off the evidence instead of repeating the failure.
Do not start additional workers simply for speed or duplicate research already
captured in the task. No fixed model names or pricing assumptions are required.

This protocol changes this repository only. The six website/Found-Ry workstreams
retain their own owners and repositories. Skillz was supplied as shared context;
its presence does not authorize an additional workstream.

## Shared task record

Use one GitHub issue or PR as the shared task record, with a single maintained
status summary. Existing Replit tasks should link that record. If a worker lacks
connector access, prepare the same public-safe handoff as text for the owner to
relay. Do not claim another platform has received or accepted work without
confirmation. A local note or branch alone is not cross-platform coordination.

Before editing, read the latest record and claim a bounded task. Record the
worker identity, platform, branch, base SHA, affected paths, and acceptance
criteria. The coordinating owner confirms conflicting or overlapping claims.
Workers must not edit shared files concurrently. Use separate branches or
worktrees for independent work; do not share an index or working directory.

Only the named integration owner updates the integration branch and performs
its final merge. A handoff needs an explicit release by the previous owner and
acceptance by the next owner. If the previous worker cannot be reached, retain
its work and request owner reassignment. Elapsed time alone is not a lease expiry.
Do not interrupt active Replit reconciliation by independently taking over its
branch. Read-only review can proceed against a recorded SHA.

## Handoff template

Copy this into the shared record when claiming, pausing, or transferring work:

```text
Task / issue / PR:
Status: proposed | claimed | working | ready-for-review | blocked | handed-off | complete
Worker and platform:
Integration owner:
Updated at (UTC):
Objective and acceptance criteria:
Allowed paths / excluded work:
Base commit / current commit / branch:
Working-tree state and preserved local-only work:
Completed changes:
Checks: command, environment, tested SHA, result, evidence link
Open findings and failed approaches:
Next exact action:
Blocker or required access:
Handoff from / to / acceptance:
```

Keep updates compact. Link relevant diffs and logs rather than pasting whole
conversation histories. Public issues, PRs, logs, and handoffs must not contain
secrets, client source, private drafts, database contents, or private account
locators. Keep necessary sensitive evidence in an approved private location.

## Integration and verification

1. Inspect status and preserve unique work, then fetch origin without initial
   pruning. Record branch divergence. Never print embedded remote credentials.
2. Fast-forward when sufficient. Reconcile genuine divergence on an isolated
   branch, preserving intent and checking whether patches are already upstream.
   Do not force-push or reset away another worker's work.
3. Review the diff and run checks appropriate to changed paths. Evidence records
   must identify their tested commit and environment. Reuse unchanged evidence
   as context; it does not establish acceptance of a different final tree.
4. Run required final integration checks and CI. Repeat checks only after a
   relevant change, a failure, or an explicit release requirement. A passed
   local check does not prove Replit behavior or hosted deployment.
5. Merge within the user's authorization, fetch again, and verify local main
   and origin/main have identical SHAs and ahead/behind counts of 0 and 0.
   Replit must independently confirm its own checkout after pulling.
6. Retire task branches only when merged or otherwise durably preserved. Report
   uncertain historical branches and unrelated work instead of deleting them.

On quota or access failure, checkpoint and release a bounded task for a worker
with available capacity. Do not purchase capacity, switch to paid execution, or
poll indefinitely. Reassignment does not grant access to another account.

## Public source and private runtime

The owner intentionally made all three Found-Ry source repositories public.
This does not make local application data or protected child capabilities public.
Keep private child defaults and permanent-private locks intact. Never commit
`.foundry-data/`, SQLite state, secrets, or client source as collaboration evidence.

The AskJamie workbench remains a loopback-only, single-user application.
Collaboration between development agents does not add multiuser application
support or authorize public Replit preview exposure. Hosting and access control
require their own scoped design and validation.
