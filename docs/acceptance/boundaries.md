# Boundary Acceptance

This note records the F09-F12 acceptance coverage for the local AskJamie Found-Ry workbench.

## Scope

- F09: malformed JSON bodies and exact request-size boundaries
- F10: local host and origin checks, write headers, and unsupported methods
- F11: decision graph cycles, unreachable nodes, and incomplete preview answers
- F12: protected update invariants plus export retention for client identity and aj03 variants

## Executable Coverage

- `tests/test_boundary_acceptance.py`

## Notes

- The existing `tests/test_workbench.py` file already covers adjacent lower-level checks such as duplicate JSON fields, transfer-encoding rejection, dangling graph edges, and export isolation.
- This acceptance note focuses on the boundary-specific end-to-end cases requested for the issue claim.
