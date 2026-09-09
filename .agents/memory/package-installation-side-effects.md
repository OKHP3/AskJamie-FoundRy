---
name: Package installation side effects
description: Environment-specific effects to check when installing development tooling.
---

Package-manager installs can update project metadata and dependency files as a side effect, even when the requested tool belongs only to CI or local development.

**Why:** Installing browser tooling in this workspace added Nix packages to `.replit` and appended the dependency to the runtime requirements file, creating unrelated project changes.

**How to apply:** Keep optional browser or test tooling in its own pinned requirements file, and review `git status` plus dependency/config diffs immediately after package installation.