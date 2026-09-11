# Workbench Usability Acceptance

Scope: F13-F16 from issue 6.

## What Was Checked

- Keyboard-only navigation and focus order in the workbench shell.
- Narrow-screen layout at 320px, 390px, and 768px.
- Save, error, and status feedback visibility and accessibility.
- Empty, loading, and stale-save recovery states.
- Navigation-away protection for unsaved draft edits.

## Browser Evidence

- Desktop shell rendered cleanly with no horizontal overflow.
- 390px, 320px, and 768px views stayed within the viewport width.
- Keyboard focus reached visible controls without trapping.
- Loading state now shows a visible workbench banner during delayed startup.
- Stale-save conflicts now show a recovery panel with a reload action.
- Canceling the unsaved-changes prompt keeps the editor in place.
- Confirming navigation away leaves without saving but preserves the dirty draft when returning.

## Findings

1. Loading feedback was too implicit during delayed startup.
2. Save and recovery feedback was visible, but not consistently announced to assistive tech.
3. Stale-save conflicts only surfaced as a raw error before the draft could be recovered.
4. Dirty draft navigation needed explicit evidence for both canceling and confirming the leave prompt.

## Fix Applied

- Added visible loading banners for initial workbench startup and project reopen flows.
- Added live-region and status semantics for save, notice, and recovery messages.
- Added a recovery action that reloads the saved copy after a stale save conflict.
- Added browser evidence for both dismissing and accepting the unsaved-changes navigation prompt.

## Reproducible Check

Run the browser script:

`tests/browser/workbench-usability.py`

It starts an isolated workbench server, checks loading and narrow-screen behavior, exercises keyboard focus, saves a project, forces a stale-save conflict followed by recovery, and verifies both branches of navigation away from dirty draft work.
