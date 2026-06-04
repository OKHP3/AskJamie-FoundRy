## Summary

<!-- What does this PR do? 1–3 sentences. -->

## Type of Change

- [ ] New capability scaffold (`_template/` or `registry/` addition)
- [ ] Registry update (`registry/index.yaml` change)
- [ ] Schema change (`schemas/`)
- [ ] Governance or documentation update (`docs/`, `AGENTS.md`)
- [ ] Archive / migration (moving legacy content)
- [ ] GitHub automation change (`.github/workflows/`)
- [ ] Scripts update (`scripts/`)
- [ ] Other: ___

## Checklist

### All PRs
- [ ] `CHANGELOG.md` updated with a description of this change.
- [ ] No secrets, credentials, or PII included.
- [ ] No client-sensitive content exposed in a public-candidate location.

### If a `manifest.yaml` was created or changed
- [ ] Ran `python3 scripts/validate-manifest.py path/to/manifest.yaml` — passes.
- [ ] Lineage fields (`parent_foundry`, `parent_repo`) are correct.
- [ ] Visibility fields match intended exposure.
- [ ] `updated` date set to today.

### If `registry/index.yaml` was changed
- [ ] Ran `python3 scripts/check-registry.py` — passes.
- [ ] Status accurately reflects the current state of the repo.
- [ ] `triage.md` updated if this resolves a triage item.

### If a schema was changed
- [ ] Version implications documented (breaking vs. non-breaking).
- [ ] Existing child repo manifests still validate (or a migration path is described).

### If a `_template/` file was changed
- [ ] Changes are backward-compatible with existing child repos, OR
- [ ] Migration note added to `docs/migration-guide.md`.

## Related Issues

<!-- Link any related issues: Closes #N, Related to #N -->

## Notes for Reviewers

<!-- Anything a reviewer needs to know that isn't obvious from the diff. -->
