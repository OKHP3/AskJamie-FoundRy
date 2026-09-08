# Original F01-F24 task coverage

Assessment date: 2026-09-08. This note maps the original 24 AskJamie Found-Ry
proposal tasks from the [website proposal packet](https://github.com/OKHP3/AskJamie/blob/171bf5c/assets/docs/coop-pertition-agent-backlog-2026-09-07.md)
to the current repository evidence on or after `main@3ea4316`.

## Scope note

The original F01-F24 queue was an upstream proposal, not the later issue-6
commissioned numbering. That later queue reused some labels for different work.
This note preserves the original meaning only. Partial proposal coverage is
future backlog, not an unresolved issue-6 assignment or an archive blocker.
The commissioned F01-F20 dispatch is complete in merged PRs #7 through #11.

Status key:

- `complete` means the repository now contains direct source/test/pilot evidence
  for the original task shape.
- `partial` means the repo shows the core contract or adjacent evidence, but
  not the full original end-to-end claim.
- `open` means no direct evidence was found in this checkout.

## Coverage matrix

| ID | Status | Current evidence | Minimal remaining gap |
| --- | --- | --- | --- |
| F01 | complete | `docs/current-state-and-maturation.md`, `docs/research/2026-09-07-universe/validation.md`, `tests/test_workbench.py`, `tests/test_registry_validation.py` show the baseline, current scope, and current local validation results. | None for the original mapping. Keep baseline notes dated if they drift. |
| F02 | complete | `AGENTS.md`, `replit.md`, `docs/workbench.md`, and `docs/current-state-and-maturation.md` now consistently separate public source, local runtime, and non-production maturity. | No specific contradiction is established in the core guidance. A speculative wording sweep is not an outstanding task. |
| F03 | complete | `schemas/manifest.schema.yaml`, `schemas/registry.schema.yaml`, and `tests/test_registry_validation.py` cover schema parity and private-lock restrictions. | None for the original mapping. |
| F04 | complete | `workbench/service.py` plus `tests/test_workbench.py` cover `repo_name()` and `validate_project()` boundaries, including aj03 and client-overlay rules. | None for the original mapping. |
| F05 | complete | `workbench/service.py`, `tests/test_workbench.py`, and `tests/test_export_acceptance.py` prove generated template rendering, provenance, and `ABOUT.md` exclusion. | None for the original mapping. |
| F06 | complete | `workbench/model.py` and `tests/test_workbench.py` cover draft normalization, non-finite numbers, unknown fields, and JSON-shape limits. | None for the original mapping. |
| F07 | complete | `workbench/model.py`, `tests/test_workbench.py`, and `tests/test_boundary_acceptance.py` cover graph cycles, dangling edges, unreachable nodes, and invalid preview answers. | None for the original mapping. |
| F08 | complete | `workbench/service.py`, `tests/test_workbench.py`, and `tests/test_export_acceptance.py` cover honest evaluation semantics, blank responses, literal matching, and the offline runner escaping contract. | None for the original mapping. |
| F09 | complete | `tests/test_workbench.py`, `tests/test_boundary_acceptance.py`, and `tests/test_recovery_acceptance.py` cover stale writes, revision history, and conflict handling. | None for the original mapping. |
| F10 | complete | `tests/test_workbench.py` and `tests/test_boundary_acceptance.py` cover revision lineage, evaluation persistence, and export evidence staying tied to the checked revision. | None for the original mapping. |
| F11 | complete | `tests/test_workbench.py` and `tests/test_boundary_acceptance.py` cover irreversible protection controls and blocked downgrade attempts. | None for the original mapping. |
| F12 | complete | `tests/test_workbench.py` covers private state permissions on POSIX, and `tests/test_boundary_acceptance.py` covers protected export retention. | Windows ACL behavior remains intentionally untested, but that was never claimed. |
| F13 | complete | `docs/acceptance/usability.md`, `docs/acceptance/usability/proposed-patch.md`, and `tests/browser/workbench-usability.py` cover keyboard focus, visible status, and recovery messaging. | None for the original mapping. |
| F14 | complete | `docs/acceptance/usability.md` and `tests/browser/workbench-usability.py` cover 320px, 390px, and wider narrow-screen layout behavior. | None for the original mapping. |
| F15 | complete | `docs/acceptance/exports.md`, `tests/test_export_acceptance.py`, and `docs/research/2026-09-07-universe/validation.md` cover the exported decision runner in a permitted local browser context. | None for the original mapping. |
| F16 | complete | `tests/test_workbench.py` and `docs/workbench-contract.md` cover honest evaluation results, missing supplied responses, and literal case-sensitive matching. | None for the original mapping. |
| F17 | complete | `docs/skillz-snapshot-refresh.md`, `docs/acceptance/onboarding.md`, and `docs/current-state-and-maturation.md` cover the controlled snapshot refresh contract and provenance boundaries. | None for the original mapping. |
| F18 | complete | `tests/test_recovery_acceptance.py` and `docs/acceptance/recovery.md` cover backup, restore, revision, and evaluation preservation. | None for the original mapping. |
| F19 | complete | `docs/acceptance/usability.md`, `docs/acceptance/usability/proposed-patch.md`, and `tests/browser/workbench-usability.py` cover keyboard journeys and announced feedback. | Human screen-reader verification remains outside this synthetic evidence set. |
| F20 | complete | `docs/acceptance/usability.md` and `tests/browser/workbench-usability.py` cover narrow-screen layout at 320px and 390px, plus desktop comparison. | None for the original mapping. |
| F21 | partial | `docs/acceptance/usability.md`, `docs/acceptance/usability/proposed-patch.md`, and `tests/browser/workbench-usability.py` show stale-save recovery and cancel/leave behavior. | A dedicated unsaved-navigation regression is still the clearest missing proof if someone wants the full original wording exercised separately. |
| F22 | complete | `docs/acceptance/pilots/assistant.md`, `docs/acceptance/pilots/assistant.json`, and `docs/acceptance/onboarding.md` define and export a synthetic assistant pilot. | None for the original mapping. |
| F23 | complete | `docs/acceptance/pilots/decision-tool.md`, `docs/acceptance/pilots/decision-tool.json`, and `docs/acceptance/exports.md` define and export a synthetic decision-tool pilot. | None for the original mapping. |
| F24 | complete | `docs/acceptance/pilots/workflow.md`, `docs/acceptance/pilots/workflow.json`, and `docs/acceptance/onboarding.md` define and export a synthetic workflow pilot. | None for the original mapping. |

## Summary

Current evidence makes the original queue mostly complete in-repo:

- Complete: F01-F20, F22-F24
- Partial future proposal: F21
- Open: none

F21 is optional future regression coverage. Stale-save recovery is not proof
of unsaved-navigation protection. This mapping does not commission that work
or expand the completed acceptance assignment.

## Verification run

I ran the current repository checks from this tree after creating a disposable
virtual environment for the pinned dependencies:

```bash
python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/check-registry.py
python3 -m unittest tests.test_workbench tests.test_registry_validation tests.test_export_acceptance tests.test_boundary_acceptance tests.test_recovery_acceptance -v
```

Results:

- `validate-manifest.py`: pass
- `check-registry.py`: pass after installing the pinned `jsonschema` dependency in the disposable venv
- `unittest`: pass, 31 tests

The host system Python initially lacked `jsonschema`, so I used a temporary
`.venv/` to run the suite against the same checkout without changing tracked
files.
