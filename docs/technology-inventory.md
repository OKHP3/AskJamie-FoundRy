# Technology inventory and update policy

Inventory baseline assembled 2026-09-18 America/Chicago; its linked sources were
retrieved 2026-09-19 UTC. The automated release watch was rerun 2026-09-26 UTC.
Question: what does this solution use, how current is it, and how will later
stable releases reach it with evidence of compatibility?

## Scope and evidence

The canonical GitHub/Windows baseline for this refresh is
`b5c7bba260e5e4a415249d7ffc65dcbf94aa3a3a`. The starting checkout was clean.
All tracked filenames, manifests, active/reference workflows, application
imports, browser assets, Replit configuration and executable skill helpers
were inspected. Private state was not read.

The application uses Python, SQLite, and plain HTML/CSS/JavaScript. There is
no root Node package manifest, lockfile, frontend build, CDN script, or external
font dependency. **TypeScript, Vite, Tailwind, React, Next.js and pnpm are not
application dependencies.** Mentions in mentor/skill guidance do not constitute
installation. Their in-place application version is not applicable.

On 2026-09-26, Replit's Git panel and Shell were inspected read-only. Both showed
clean `main` at `b5c7bba260e5e4a415249d7ffc65dcbf94aa3a3a`, equal to
`origin/main` with `0/0` divergence and no changes to commit. The Replit project
also has an unrelated ongoing agent task; it was left untouched. This confirms
source parity at the observation time, not parity of installed host packages or
Replit connector authentication.

The linked latest-version entries are the source ledger. Publishers are
upstream maintainers, official package registries or standards bodies. Each
link supports the release/specification in its row, retrieved on the date
above. These are dated observations, not perpetual latest-version claims.

## Application and test stack

| Technology | In place / evidence | Latest stable and primary source | Update route |
|---|---|---|---|
| Python / CPython | Required CI floor `3.11`; a separate CI job follows latest stable `3.x`. Project guidance reports successful verification under `3.11.15` and `3.14.5`. This Windows audit process itself reports **3.14.0rc1**, a prerelease, and is not the stable runtime baseline. | [3.14.7; 3.11 line 3.11.16; 3.12 line 3.12.14](https://www.python.org/downloads/) | Latest stable CI plus separately validated host migrations |
| Python standard library | `http.server`, `sqlite3`, `json`, `zipfile`, `hashlib`, `urllib`, `unittest`, `venv`, etc. follow the interpreter | [Same Python release](https://docs.python.org/3/library/) | Update Python; no individual pip pins. HTTP server remains loopback-only. |
| PyYAML | `6.0.3` pinned in `requirements.txt`, installed on both hosts | [6.0.3](https://pypi.org/project/PyYAML/) | Current; Dependabot PRs |
| jsonschema | `4.26.0` pinned in `requirements.txt`, installed on both hosts | [4.26.0](https://pypi.org/project/jsonschema/) | Current; Dependabot PRs |
| SQLite | Windows Python `3.49.1`; Replit Python `3.51.1`; used by `workbench/store.py` | [3.53.4](https://sqlite.org/changes.html) | Python/host distribution, then backup/import and transaction tests |
| LibYAML | PyYAML extension `0.2.5` observed on both hosts; `.replit` also declares unpinned `libyaml` | [0.2.5](https://github.com/yaml/libyaml/releases/tag/0.2.5) | PyYAML wheel/Nix package; declaration does not prove system library bytes |
| OpenSSL | Windows Python `3.0.16`; Replit Python `3.6.0` | [4.0.2; supported 3.6 line 3.6.4; 3.5 LTS line 3.5.8](https://openssl-library.org/source/) | Python/host distribution security updates. Do not manually replace interpreter libraries. 4.1.0-alpha1 excluded. |
| zlib / zlib-ng | Stable audit Python zlib `1.3.1`; prerelease Python `1.3.1.zlib-ng` compatibility string; actual zlib-ng release unknown | [zlib 1.3.2](https://zlib.net/); [zlib-ng 2.3.3](https://github.com/zlib-ng/zlib-ng/releases/tag/2.3.3) | Python distribution; ZIP export/import tests |
| Playwright for Python | `1.63.0` pinned in `tests/browser/requirements.txt`; merged in [PR #21](https://github.com/OKHP3/AskJamie-FoundRy/pull/21). The current Replit checkout reports 81 passing Python tests. | [1.63.0](https://pypi.org/project/playwright/) | Current; Dependabot proposes later releases for review and browser acceptance |
| Playwright Chromium/headless shell | Pinned Playwright 1.63.0 browser manifest: `153.0.8010.12`, revision `1243`; CI installs Chromium | [1.63.0 browser manifest](https://github.com/microsoft/playwright/blob/v1.63.0/packages/playwright-core/browsers.json) | Install browsers paired with Playwright. This is its tested build, not consumer Chrome stable. Actual overrides remain host-specific. |
| Playwright auxiliary binaries | Pinned 1.63.0 manifest: FFmpeg revision `1011`, Windows helper revision `1007`, Firefox `155.0` revision `1543`, WebKit `26.6` revision `2359` (macOS 14 override `2251`); Firefox/WebKit are not installed by this CI workflow | [1.63.0 browser manifest](https://github.com/microsoft/playwright/blob/v1.63.0/packages/playwright-core/browsers.json) | Managed with Playwright; revision IDs are not upstream semantic versions |

The isolated Windows audit venv was created with Python 3.12.10 and both
existing requirements files. It is validation evidence; the default interpreter
was not upgraded.

## Resolved Python packages

These are indirect dependencies, except pip which is installation tooling.
No transitive lockfile is checked in. Fresh installs resolve parent constraints.

| Package | Windows audit venv | Replit observed | Latest stable / source | Constraint |
|---|---|---|---|---|
| attrs | 26.1.0 | 26.1.0 | [26.1.0](https://pypi.org/project/attrs/) | jsonschema/referencing |
| jsonschema-specifications | 2025.9.1 | 2025.9.1 | [2025.9.1](https://pypi.org/project/jsonschema-specifications/) | jsonschema |
| referencing | 0.37.0 | 0.37.0 | [0.37.0](https://pypi.org/project/referencing/) | jsonschema |
| rpds-py | 2026.6.3 | 2026.5.1 | [2026.6.3](https://pypi.org/project/rpds-py/) | Python/Rust binary wheel; no solution-owned Rust build toolchain |
| typing-extensions | 4.16.0 | Not reported by initial probe | [4.16.0](https://pypi.org/project/typing-extensions/) | Conditional referencing dependency and pyee dependency; probe omission does not establish absence |
| pyee | 13.0.1 | 13.0.1 | [14.0.0](https://pypi.org/project/pyee/) | Playwright 1.63.0 requires `<14,>=13`; do not force 14 |
| greenlet | 3.5.6 | 3.5.5 | [3.5.6](https://pypi.org/project/greenlet/) | Playwright permits `>=3.1.1,<4` |
| pip | 25.0.1 | 25.0.1 | [26.2.1](https://pypi.org/project/pip/) | Host tooling; prerelease Windows Python separately had 25.1.1 |

The audit checks these indirect packages when installed. Newer upstream
versions are informational `AVAILABLE` entries, not permission to override
parent constraints. CI records `requirements-resolved.txt` for each run.
That freeze is evidence for that Python/OS combination, not a universal lock.

## Browser standards, formats and documentation

| Technology | In-place contract | Current stable specification / source | Update route |
|---|---|---|---|
| JavaScript / ECMAScript | Native scripts, async/await; no compiler target | [ECMAScript 2026, ECMA-262 edition 17](https://ecma-international.org/publications-and-standards/standards/ecma-262/) | Browser tests; no installable language package |
| HTML / DOM / Fetch / Web Storage | HTML doctype, native DOM/Fetch/localStorage APIs | [WHATWG living standards](https://spec.whatwg.org/) | No numeric pin; test behavior and storage recovery |
| CSS | Handwritten Grid/Flexbox/custom properties/media queries | [CSS Snapshot 2026](https://www.w3.org/TR/css-2026/) | Module-specific standards, not one upgradeable package |
| SVG / XML | Favicon and inline SVG noise texture, no renderer pin | [SVG 1.1 Second Edition recommendation](https://www.w3.org/TR/SVG11/); [SVG 2 candidate recommendation](https://www.w3.org/TR/SVG2/) | Browser rendering; no claim of SVG 2 conformance |
| YAML | No version directive; PyYAML loader semantics, separate GitHub workflow parser | [YAML 1.2.2](https://yaml.org/spec/1.2.2/) | Validate parser behavior; no inferred YAML 1.2 conformance |
| JSON / JSONL | Python/browser serialization and line-delimited diagnostics | [JSON RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) | Serialization and diagnostic regression checks |
| JSON Schema | Explicit Draft 2020-12 in both schemas | [Draft 2020-12](https://json-schema.org/specification) | Current; deliberate schema migrations |
| TOML | `.replit` uses TOML 1.0-compatible syntax; platform parser unknown | [TOML 1.1.0](https://toml.io/en/) | Use Replit-supported syntax |
| Markdown / GFM | Documentation/export text; renderer unpinned | [CommonMark 0.31.2](https://spec.commonmark.org/); [GFM 0.29-gfm](https://github.github.com/gfm/) | Viewer-managed; preview changed documents |
| Mermaid | Fences in `docs/ecosystem-map.md` and `threat_model.md`; no bundled library | [12.0.0](https://registry.npmjs.org/mermaid/latest) | GitHub manages its renderer; its installed version was not measured |
| ZIP / DEFLATE | Python `zipfile` exports/backups | [Python zipfile contract](https://docs.python.org/3/library/zipfile.html) | Follows Python/zlib, verify export/restore |

PDF/DOCX files are reference assets, not installed document engines. Skillz
catalog and Agent Skill versions are content provenance. The locked AutoCAD
R10 content constraint remains unchanged and is not an upgrade target.

## CI, hosting and development environment

Active workflows use major tags, which float within that line. Latest releases
below do not establish an earlier run's resolved SHA or embedded Node engine.

| Technology | In-place reference | Latest stable / primary source |
|---|---|---|
| actions/checkout | v7 | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) |
| actions/setup-python | v7 active; v6 in inactive reference workflows | [v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0) |
| actions/configure-pages | v6 | [v6.0.0](https://github.com/actions/configure-pages/releases/tag/v6.0.0) |
| actions/upload-pages-artifact | v5 | [v5.0.0](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0) |
| actions/deploy-pages | v5 | [v5.0.1](https://github.com/actions/deploy-pages/releases/tag/v5.0.1) |
| actions/upload-artifact | v7 | [v7.0.1](https://github.com/actions/upload-artifact/releases/tag/v7.0.1) |
| GitHub Actions / Pages / Dependabot | Managed services; runner `ubuntu-latest`; Dependabot config schema 2 | [Runner images](https://github.com/actions/runner-images); [Dependabot configuration](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file), no customer-controlled SaaS version |
| Replit | Managed workspace, no platform pin | [Replit configuration reference](https://docs.replit.com/replit-app/configuration) |
| Nixpkgs channel | `.replit`: `stable-25_05` | [Upstream 26.05](https://nixos.org/blog/announcements/2026/nixos-2605/) |
| Nix | Replit reports Nix 2.31.1 with Determinate Nix 3.11.2 | [Upstream stable manual 2.34.9](https://nix.dev/manual/nix/stable/); [Determinate fork v2.35.2](https://github.com/DeterminateSystems/nix/releases/tag/v2.35.2) |
| Node.js | Replit module `nodejs-24`; Windows/Replit versions `24.13.0` / `24.11.1` were observed in the dated source inventory, not re-probed in this refresh | [LTS 24.21.0; stable Current 26.10.0](https://nodejs.org/dist/index.json) |
| npm | Windows/Replit `11.6.2` in the dated source inventory, not re-probed in this refresh; seven skill package manifests have no third-party dependencies | [12.1.0](https://registry.npmjs.org/npm/latest) |
| PostgreSQL | Replit module `postgresql-16`, CLI 16.10; no application driver/import/query dependency | [18.6; 16 line 16.15](https://www.postgresql.org/docs/release/) |
| Bash | Replit 5.2.37; post-merge and CI scripts | [5.3](https://www.gnu.org/software/bash/manual/bash.html), [patches through 020](https://ftp.gnu.org/gnu/bash/bash-5.3-patches/) |
| Git | Windows 2.55.0.windows.5; Replit 2.50.1 | [2.55.0](https://git-scm.com/); [Windows 2.55.0.windows.5](https://github.com/git-for-windows/git/releases/tag/v2.55.0.windows.5) |
| GitHub CLI | Windows 2.96.0, developer tool only | [2.101.0](https://github.com/cli/cli/releases/tag/v2.101.0) |
| PowerShell | Windows 7.6.5, developer shell only | [7.6.6](https://github.com/PowerShell/PowerShell/releases/tag/v7.6.6) |

Nix and Determinate numbers have different distribution identities; do not
compare them as one sequence. Upstream Nixpkgs availability does not prove
Replit accepts a corresponding channel name. Node supports optional skill
helpers, not the server. Seven private `@bp-skill` packages are at 0.1.0 with
Node built-in tests. Other skill helpers use Node/Python built-ins and existing
YAML/schema tooling. Editors and AI clients are not deployed dependencies.

## Implemented tracking

1. **Daily dependency PRs:** `.github/dependabot.yml` covers root requirements,
   browser-test requirements and active Actions. Playwright is now explicitly
   covered. New major versions remain eligible for review.
2. **Latest stable Python CI:** the required `Validate with supported Python
   runtime` retains 3.11 with `check-latest: true`. A separate job uses `3.x`,
   `check-latest: true`, `allow-prereleases: false`, and executes validators,
   the public artifact build and unit tests. It follows new stable interpreters
   automatically. The full compatibility workflow also runs weekly/manually.
3. **Daily release watch:** `technology-watch.yaml` executes
   `scripts/audit-technologies.py` for direct packages, active Actions,
   installed indirect packages and `.github/technology-watch.json` upstreams.
   It saves a summary, JSON and per-run dependency freeze for 30 days.
   Scheduled/manual runs fail visibly on `UPDATE`, `REVIEW` or `UNKNOWN`.
   PR runs tolerate known version gaps but fail unknown lookups. Notifications
   depend on the owner's GitHub Actions notification settings.
4. **Monthly owner review plan:** inspect the remaining links for Replit
   channel availability, PostgreSQL metadata, Nix/Determinate, host tools,
   standards and viewer-managed rendering. This is a plan, not a scheduled
   reminder or automatic installer. Review inactive workflow examples before
   activation. Consider removing unused PostgreSQL metadata in a separate task
   after confirming Replit has no other use for it.

Schedules and Dependabot configuration activate after merging to the default
branch. GitHub can delay jobs and disable schedules in inactive public repos
after 60 days, so monthly review includes checking Actions are enabled.
[GitHub schedule behavior](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule).

Watch baselines are **reviewed upstream versions, not installed versions**.
`REVIEWED` does not clear older host versions. Advance a baseline only with
a recorded disposition and relevant tests. Failed lookups, changed page
formats, unsupported versions or missing stable releases report `UNKNOWN`.

On 2026-09-26, the release watch reported Node.js Current `26.10.0` and npm
`12.1.0`, up from the prior observed baselines. The reviewed baselines now record
those releases. This accepts the upstream observations only: `.replit` remains
on the Node.js 24 LTS module, npm is optional developer tooling, and no host
runtime or application dependency was upgraded. npm `12.1.0` declares support
for Node `^24.15.0`; the watched Node LTS `24.21.0` satisfies that range. The
latest pyee `14.0.0` remains incompatible with Playwright's `pyee>=13,<14`
constraint and is not adopted. `AVAILABLE` pip `26.2.1` remains host tooling,
not an application dependency update.

## Migration and merge plan

The integration owner follows this sequence for every update:

1. Inspect release notes, parent constraints and interpreter requirements.
   Claim affected paths and use a task branch. Keep major migrations separate.
2. Before host changes, stop the workbench and preserve its private data.
   Build a fresh environment with the chosen stable Python, both requirements
   files, and the matching Playwright Chromium build.
3. Run manifest/registry validators, public artifact build, all unit tests,
   exported decision browser acceptance and workbench usability. Confirm
   boundary, backup/import, protection flags and failure diagnostics.
4. Require the supported Python check and review **all** compatibility/browser
   results before owner merge. Latest-Python CI is an added job, not a new
   branch-protection rule. No auto-merge is enabled; zero external approvals
   remain the existing solo-owner policy.
5. Fast-forward Windows and Replit only after Replit's existing owner releases
   or integrates its pending work. Recreate environments as needed and record
   versions/tests independently on both hosts. Git equality is insufficient.
6. Update this inventory and review baselines with evidence. Keep a failed
   update open and retain known-good pins. Revert a bad merged update through
   a PR; restore private state only from a verified backup when needed.

Pages remains manually dispatched and separately authorized. No tracking
change enables public authoring or uploads private state.

## Commands and interpretation

With the documented virtual environment active:

```bash
python scripts/audit-technologies.py --environment-only
python scripts/audit-technologies.py
python scripts/audit-technologies.py --fail-on-change
```

Reports default to ignored `.local/technology-audit/report.{json,md}`. An
existing `GH_TOKEN` can authenticate GitHub API reads to avoid anonymous rate
limits; never put tokens in source/logs/handoffs. CI uses its ephemeral
read-only token. Exit 0 means lookups completed, not all versions are current.
With `--fail-on-change`, exit 1 means updates/review are pending. Exit 2 means
unknown evidence. The environment report includes the Python release level,
bundled libraries, package versions and Playwright browser manifest.

| Claim | Tier | Evidence / next check |
|---|---|---|
| Two application and one browser package are pinned | Confirmed | Requirements and imports; rediscovered each audit |
| No application TypeScript/Vite/Tailwind stack | Confirmed | Tracked manifests/entry points searched; repeat inventory when new stack files appear |
| Latest versions listed above | Confirmed at retrieval | Primary sources per row; live watch and monthly review |
| Replit source matches GitHub | Confirmed at 2026-09-26 observation | Git panel and Shell both showed clean `main` at `b5c7bba260e5e4a415249d7ffc65dcbf94aa3a3a`, `0/0` |
| Upgrades are compatible | Proposal until tested | Version numbers alone do not prove compatibility |
| Earlier CI patch versions, viewer renderer, unreported host libraries | Unknown | Capture the specific run/host rather than infer from selectors |

Next action: retain monthly review of the dated standards, managed services and
host-tool entries above; confirm host versions only when those environments are
independently inspected.
