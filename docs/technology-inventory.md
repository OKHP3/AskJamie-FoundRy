# Technology Inventory and Update Policy

Updated: 2026-07-20

This repository is a governance workbench, not a web application. It does not
contain TypeScript, JavaScript, Vite, Tailwind, React, npm, or a frontend build.

## Technologies in use

| Technology | In-place version or state | Latest stable checked | Evidence or source |
|---|---|---|---|
| Python | 3.11 declared for the utilities and Replit; repository history records 3.14.5, current Windows launcher reports 3.14.0rc1 | 3.14.6 | `scripts/README.md`, `.replit`, `AGENTS.md`; [Python downloads](https://www.python.org/downloads/) |
| PyYAML | Previously unpinned; now pinned to 6.0.3 | 6.0.3 | `requirements.txt`; [PyYAML on PyPI](https://pypi.org/project/PyYAML/) |
| jsonschema | Previously optional and unpinned; now pinned to 4.26.0 | 4.26.0 | `requirements.txt`; [jsonschema on PyPI](https://pypi.org/project/jsonschema/) |
| YAML | YAML configuration and data files, parsed by PyYAML | PyYAML follows its own release line | `*.yaml`, `*.yml`; [PyYAML](https://pyyaml.org/) |
| JSON Schema | Draft 2020-12 | Draft 2020-12 | `schemas/*.schema.yaml`; [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) |
| GitHub Actions | Staged workflows plus the active compatibility workflow | Action references: checkout 7.0.1 line via `@v7`, setup-python 6.2.0 line via `@v6` | `.github/workflows/`, `docs/github-workflows/`; [checkout releases](https://github.com/actions/checkout/releases), [setup-python releases](https://github.com/actions/setup-python/releases) |
| Nix/Replit environment | Nix channel `stable-25_05`, package `libyaml` | NixOS/Nixpkgs 26.05 is the current stable line | `.replit`; [NixOS stable releases](https://nixos.org/manual/nixos/stable/release-notes) |
| Markdown | Repository documentation format | No single universal package version is pinned | `*.md`; CommonMark-compatible GitHub rendering |
| PDF and DOCX | Reference/document artifact formats, not executable dependencies | Format versions are not pinned in this repository | `assets/`; historical capability files are no longer present |

## Deliberately absent

There are no package manifests for npm, TypeScript, JavaScript, Vite,
Tailwind, React, Vue, Next.js, or other web frameworks. No version should be
reported for those technologies as part of this solution.

## Update policy

1. Dependabot checks `requirements.txt` and GitHub Actions every week.
2. Pull requests may update PyYAML, jsonschema, and action references.
3. The compatibility workflow installs the pinned dependencies and runs the
   canonical manifest and registry checks before an update can merge.
4. Python remains on the supported 3.11 line until a maintainer explicitly
   approves a runtime migration. A Python 3.14 upgrade should be tested as a
   separate change because it is a runtime-policy decision, not a patch update.
5. Nix channel upgrades remain Replit/environment changes and require a
   deliberate `.replit` update with a follow-up validation run.

Dependabot configuration is active in `.github/dependabot.yml`. The older
workflow definitions under `docs/github-workflows/` remain staged reference
files, but their action references are kept aligned with the active workflow.
