# Proposed Patch: Workbench Usability

This patch consolidates the workbench usability fixes for F13-F16.

## Changed Surfaces

- `workbench/static/app.js`
- `workbench/static/styles.css`
- `workbench/static/index.html`
- `tests/browser/workbench-usability.py`

## User-Facing Changes

- Shows a visible loading state while the workbench and project editor are fetching.
- Announces save and status feedback more reliably to assistive tech.
- Surfaces stale-save conflicts with a recovery panel and reload action.
- Keeps the workbench within viewport width at the tested narrow sizes.

## Acceptance Check

- Keyboard-only navigation stays usable.
- 320px, 390px, and 768px widths do not overflow horizontally.
- Save, error, and status messaging is visible and announced.
- Empty, loading, and stale-save recovery states are exercised by the browser script.
