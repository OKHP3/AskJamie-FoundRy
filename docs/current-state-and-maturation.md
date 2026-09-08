# AskJamie Found-Ry: current state and maturation

Assessment date: 2026-09-08. This is a project assessment, not a production certification.

## Current state

The solution is a working local alpha for building AskJamie capabilities. The repository has moved from a governance scaffold to an application with a browser editor, Python service, SQLite storage, evaluation records and governed exports. Its tested scope is deliberate: authored assistant assets, executable deterministic decisions, and guided workflow checklists.

Research and mentoring clarification landed in [PR #3](https://github.com/OKHP3/AskJamie-FoundRy/pull/3), the workbench implementation and follow-up fixes landed in [PR #4](https://github.com/OKHP3/AskJamie-FoundRy/pull/4), and the collaborative handoff guidance landed in [PR #5](https://github.com/OKHP3/AskJamie-FoundRy/pull/5). These are part of the current main-branch baseline, not pending changes.

## Relationship to the universe

OverKill Hill is the centroid and baseline pattern the distinct regional sites borrow from or defer to when a question arises. Its intentionally public Found-Ry is the mentor pattern for AskJamie Found-Ry and Glee-fully Tools Found-Ry. Mentoring can flow back to OverKill or between peers. Skillz is the shared catalog across the three regions. AskJamie owns its interpretive capabilities, private drafts and governed child packages.

This model guides future development: inspect the mentor's relevant pattern, adapt it to AskJamie, validate the result, and offer reusable improvements back through a reviewable change. It does not require identical applications or a shared runtime.

## What works today

| Area | Implemented behavior | Boundary |
|---|---|---|
| Project authoring | Create assistant, decision-tool or workflow drafts; edit purpose, audience, behavior, constraints and sources | The user supplies the substance; no AI authoring service runs |
| Persistence | Save/reopen projects, retain revision history, reject stale writes | Local single-user SQLite; no collaboration or synchronization |
| Decision tools | Author Yes/No questions and results; validate and execute paths; export HTML runner | Deterministic graph, not arbitrary code generation |
| Evaluations | Execute decision cases; record results against saved revisions; check supplied response text | Text checks do not establish model behavior or semantic quality |
| Skillz | Search 342 entries from a dated public snapshot; retain selected metadata and source provenance | Selection does not install, execute or independently validate skills |
| Export | Generate private ZIP containing scaffold, manifest, source, instructions, specification and evidence | Registration remains a pending proposal; no remote repository is created |
| Governance | Read nine canonical records, validate registry schema, preserve lineage and client protections | Registry entries do not prove deployment or operational status |
| Privacy | Loopback service, guarded JSON writes, isolated exports, irreversible client flags; owner-only POSIX state permissions | No internet-hosted authentication, encryption layer or Windows ACL management |

## Architecture and operating model

The interface uses plain HTML, CSS and JavaScript with no frontend build. Python 3.11 or newer serves the interface and API using its standard library. SQLite stores drafts, historical revisions and evaluations. PyYAML and jsonschema are the two direct pinned dependencies. No provider key, inference subscription or runtime model call is required.

State is stored in an ignored, dedicated `.foundry-data/` directory by default. On POSIX systems the app sets this directory to 0700 and the database and existing SQLite sidecars to 0600. It tightens existing state on startup. These are filesystem permissions, not encryption. On Windows, directory access must be controlled through operating-system account permissions.

Use the [operating guide](workbench.md) to start and back up the application. Stop the service before copying its state. The localhost preview is a running development process, not an installed background service or hosted deployment.

## Evidence and limitations

The initial integrated version passed 19 tests on Python 3.11.15 and 3.14.5. Follow-up review fixes add regression checks for private file modes and non-finite numbers. The current local suite passes 22 tests in the repository virtual environment. Manifest/registry validation, JavaScript syntax and diff checks pass. GitHub CI results should be checked against the current PR head before merge.

Browser acceptance covered creation, editing, saving, reopening after server restart, both decision branches, Skillz selection, two passing authored evaluations, retained history/results, ZIP download, registry names and cancel behavior. Review feedback also corrected the search toolbar and a validator return annotation.

Unverified areas remain explicit: direct browser execution of the exported local HTML was blocked by browser URL policy; narrow-screen visual QA and a full accessibility audit are incomplete. Automated checks cover the HTML's structure and escaping. No real-user pilot, external assistant evaluation, production deployment or backup-restoration acceptance has been completed. See the [validation record](research/2026-09-07-universe/validation.md).

## Recommended maturation sequence

These are proposed next steps, not completed features or promised dates.

| Order | Work | Evidence required to advance |
|---|---|---|
| 1. Stabilize the baseline | Keep the merged research, workbench, and collaboration changes on main; verify the launch guide and the local suite from a clean checkout | Main stays clean, the current local suite passes 22 tests, and startup still works |
| 2. Pilot real work | Build one useful AskJamie assistant specification, one decision tool and one workflow from owner-approved source | Each has a reviewed export, representative cases and a record of friction found during use |
| 3. Complete reliability and usability | Exercise exported HTML in an allowed browser environment; test narrow screens, keyboard and assistive technology; perform backup/restore; automate core browser journeys | Reproducible acceptance evidence, successful restore without lost source/history, no unresolved blocking usability issues |
| 4. Make mentoring operational | Compare relevant OverKill Found-Ry patterns; record adoption/adaptation decisions; propose proven AskJamie improvements to the mentor or Glee-fully; define controlled Skillz snapshot refresh | One documented round trip of a useful pattern, with provenance, validation and regional ownership retained |
| 5. Graduate a capability | Choose one target platform and implement the minimum export/import adapter needed for the pilot; review its pending registry proposal | A real child capability works on that platform, its tests are rerun there, and registration reflects verified state |
| 6. Add assistance selectively | If pilots show value, add optional model-assisted drafting/evaluation with explicit cost limits, data routing, provider abstraction and measured quality | Improvement over the manual baseline with known cost and acceptable data handling |
| 7. Choose deployment deliberately | If cross-device or team use is required, design authenticated hosting, authorization, backups, migrations and operations before Replit or other exposure | Tested access boundaries, restore/recovery procedure, ownership and deployment evidence |

The next useful milestone is a repeatable, tested AskJamie capability produced by this workbench and successfully used outside it. Feature breadth should follow that evidence. Preserve the low-cost local mode as additional integrations mature.

## Closeout verification, 2026-09-08

PRs #7 through #10 are merged. The combined baseline passed 31 Python tests.
Recovery, export, boundary and usability evidence is in `docs/acceptance/`.
The recovered F17-F20 work includes three machine-readable synthetic pilots;
all normalize, pass export readiness, and produce schema-valid private packages.
These synthetic checks do not replace an owner pilot or hosted deployment.
