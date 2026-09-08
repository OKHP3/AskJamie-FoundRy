# Recovery Acceptance

This document records the verified synthetic-data recovery procedure for the
Workbench store.

## Purpose

Confirm that a private backup can be restored without losing:

- project data
- revision history
- evaluation records

It also confirms two safety properties:

- separate data directories do not share state
- stale writes are rejected after a store restart

## Synthetic Data

Use only synthetic drafts. Do not point the acceptance run at a real private
data directory.

The acceptance tests create a small assistant draft, save one revision update,
record one evaluation, and then restore from a copied data directory.

## Verified Procedure

1. Create a fresh temporary store directory.
2. Create one synthetic project.
3. Update it once so the project has revision 2.
4. Run one evaluation so the SQLite database contains revision, history, and
   evaluation evidence.
5. Copy the complete store directory to a second location while the app is
   stopped.
6. Open the copied directory with a new `Store`.
7. Confirm the restored project still exists, its revision is 2, its history is
   `[2, 1]`, and its evaluation record is present.
8. Create a separate store in a different directory and confirm that the two
   stores do not share projects or evaluations.
9. Restart the original store and confirm a write using revision 1 raises a
   stale-revision error.

## Acceptance Check

Run the focused recovery suite from the repository root:

```bash
python3 -m unittest tests.test_recovery_acceptance -v
```

The check passes when the restore, isolation, and stale-write assertions all
hold against the synthetic store data.
