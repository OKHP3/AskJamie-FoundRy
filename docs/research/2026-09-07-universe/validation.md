# Workbench validation record

Date: 2026-09-07. Scope: private local AskJamie Found-Ry application and its governed exports.

## Automated checks

Pinned `requirements.txt` dependencies were installed into isolated virtual environments. The system `python3` alone does not have jsonschema installed and is not the validated invocation. Run the documented installation first.

- Python 3.11.15: 19 of 19 unittest tests passed.
- Python 3.14.5: 19 of 19 unittest tests passed.
- Both suites ran with `PYTHONWARNINGS=error::ResourceWarning`.
- Root manifest validation and nine-entry registry validation passed.
- Python compilation, JavaScript syntax and `git diff --check` passed.

Reproducible commands after activating the environment:

```bash
python -m pip install -r requirements.txt
PYTHONWARNINGS=error::ResourceWarning python -m unittest discover -s tests -v
python scripts/validate-manifest.py manifest.yaml
python scripts/check-registry.py
python -m compileall -q workbench tests
node --check workbench/static/app.js
git diff --check
```

Tests cover durable persistence and revision history, stale updates, irreversible client protections, malformed HTTP bodies and origin/host restrictions, graph cycles and invalid targets, unknown answer IDs, honest unrun tests, schema-valid isolated exports, script escaping, source/template provenance, and registry schema/privacy enforcement.

## Follow-up review validation

The follow-up commit adds two regression tests. The current Python 3.11.15 suite passes 21 of 21 tests, including creation/reopening of owner-only POSIX state and rejection of non-finite nested JSON numbers. The original 19-test Python 3.14.5 result above remains the earlier baseline. Search toolbar styling and the registry validator return annotation were also corrected. Manifest/registry validation, JavaScript syntax and diff checks pass.

## Browser acceptance

The in-app browser exercised the integrated Python 3.11 server with synthetic owner-original source in a separate QA database:

1. Created a decision starter through the explicit dialog.
2. Edited title and source, saved, restarted the server, and reopened the persisted project.
3. Ran both Yes and No preview paths with the expected distinct results.
4. Searched the full 342-entry Skillz snapshot and selected one evidence-standard reference without first opening the catalog screen.
5. Authored two evaluation cases with explicit answers and exact expected results. Saved revision 5 returned two passed, zero failed, zero unrun.
6. Reloaded the page and reopened the project. Latest evaluation and all five revision records persisted and rendered.
7. Validated with no errors or warnings and used Download private ZIP successfully. Independent export readback contained 26 ZIP entries, a private schema-valid manifest, and exactly one selected skill reference.
8. Verified all nine canonical registry repository names render. Canceling the create dialog left the project count unchanged.
9. Inspected desktop screenshots and repaired evaluation-row text overlap. No application-origin console error was returned by the browser log tool.

The first rendered pass caught incorrect static asset URLs and a decision-kind value mismatch. Later integration fixed strict PUT payloads, evaluation answer authoring, persisted-result reset/order, registry field names, preview restart and evidence-row layout. These are included in the application changes.

## Boundaries

Direct browser navigation to an exported `file://` HTML file was rejected by the browser URL policy. No workaround was attempted. Offline HTML structure, embedded decision data and script escaping are covered by automated checks; execution of the downloaded file in a browser is not claimed. Narrow-screen visual behavior and a full assistive-technology audit were not completed.

This evidence establishes the local builder, deterministic graph execution, supplied-response text checks and private package generation. It does not establish AI response quality, hosted GPT provisioning, autonomous code generation, Replit deployment or production multiuser access controls. Skill selection preserves public metadata and does not install or execute skill code.

The owner checkout and canonical registry entries remain unchanged. Research and implementation are reviewable branches and pull requests; merging and hosted deployment are separate actions.
