# Skillz snapshot refresh checklist

Assessment date: 2026-09-08. This is a controlled refresh note, not runtime
automation. There is no runtime execution here.

## Purpose

Refresh the bundled Skillz metadata snapshot only when there is a clear reason
to do so, and only with provenance recorded in the repo. The snapshot is a
dated reference. It is not live truth and it does not execute skills.

## When to refresh

- The source catalog commit changes.
- Entry counts or family counts drift.
- A description is clearly stale in a repo-private doc that references the
  snapshot.
- A maintainer asks for a reviewed update.

## Inputs to record first

- Source catalog URL.
- Source commit SHA.
- Retrieval date.
- Local file path for the snapshot.
- Entry count and family count.
- Any fields expected to drift, such as description text or evidence status.

## Refresh steps

1. Re-fetch the public catalog metadata from the documented source.
2. Record the source commit and retrieval date in the repo note.
3. Compare counts, families, maturity, evidence status, and descriptions against
   the previous snapshot.
4. Mark stale descriptions as stale, do not rewrite them into assumed truth.
5. Keep private sibling or child details out of the public summary.
6. Review the change in a pull request before any downstream doc update.

## Hard stops

- Do not run a skill body as part of the refresh.
- Do not treat the snapshot as a runtime dependency.
- Do not silently overwrite the old snapshot.
- Do not claim production readiness from catalog metadata alone.
- Do not auto-update any downstream workbench behavior.

## Suggested output

Record a short note with:

- source
- commit
- retrieval date
- changed counts
- changed descriptions
- privacy caveats

That is enough for a controlled refresh. Anything broader belongs in a separate
review.
