---
name: Browser acceptance executable
description: Workspace-specific Chromium selection for Playwright browser acceptance tests.
---

Playwright browser acceptance tests expect `BROWSER_EXECUTABLE_PATH` when the managed browser cache is unavailable. This workspace provides Chromium at `/repl/tools/bin/chromium`.

**Why:** The test runner can fail before any assertions if Playwright's downloaded browser is absent, even though a compatible system Chromium is available.

**How to apply:** Supply `BROWSER_EXECUTABLE_PATH=/repl/tools/bin/chromium` when running the browser acceptance tests locally; do not change project dependencies just to obtain the browser.