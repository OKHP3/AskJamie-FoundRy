# AskJamie Found-Ry workbench

Build an interpretive capability from an idea, test its decisions, and keep the
source and evidence with the result. Everything stays on this computer.

## Start

Use Python 3.11 or newer from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m workbench --port 8765
```

Open http://127.0.0.1:8765. Stop with Ctrl+C. The private interface has no build
step. The separate `public/` directory is a static, read-only Pages artifact
and never reads this server or its local state.
The application binds to loopback and makes no model-provider calls. It is a
single-user local tool, not a hosted multiuser service. Do not proxy it onto
the internet or expose it through a Replit preview without a separate access
control design.

## Build a capability

1. Create a project or choose a starter. A starter is editable sample content;
   it becomes a saved project only when you save it.
2. Define its purpose, audience, original source and source reference. Source
   references are your provenance claims, not independently verified citations.
3. Write the instructions, constraints and output contract. Choose an assistant,
   decision tool or guided workflow. Keep the scope useful and specific.
4. For a decision tool, add question and result nodes. Each question has Yes and
   No paths. Run the preview to follow a real path and inspect the result.
5. For a workflow, write an ordered sequence of steps. It exports a checklist;
   it does not run external actions.
6. Add tests. Decision tests run the graph. Assistant/workflow checks compare a
   response you supply against required and forbidden text. They never call an
   AI model; an empty response remains unrun.
7. Select helpful Skillz references, preserving each entry's family, maturity,
   evidence status and source commit. Selecting a reference does not install or
   execute a skill.
8. Save, validate and export. Resolve any naming, missing-content or graph errors.

The brief also records a planning `target` and `phase`, while Evidence records
what has been checked and what remains unknown. These labels guide review; they
do not provision a Custom GPT, call a model, or graduate a package.

## Lifecycle and recovery

From Projects, use **Download backup** to save a version-one JSON envelope
containing this workbench’s projects, complete revision history, and evaluation
records. **Import backup** requires both a browser confirmation and the server’s
explicit confirmation field. The server validates every project, revision,
history entry, evaluation reference, and supported draft field before opening a
transaction. A malformed file leaves the existing database untouched.

Saved projects can be **duplicated** into a fresh private revision-one draft.
Duplicate evaluation history is intentionally not copied. **Delete** requires a
saved project and explicit confirmation, then removes its history and
evaluations with the project. These controls never alter the canonical registry
or publish a package.

Saved revisions and evaluation runs are durable. A test run belongs to a
specific revision; editing creates a new revision and does not inherit a pass.
If a second tab has saved changes, stale updates fail instead of overwriting
its work. Reopen the saved version to reconcile before saving again.

## What a package contains

The ZIP starts from the canonical `_template/` layout and includes a valid
manifest, source, instructions, specification, test cases, selected skill
metadata, evaluation records and a pending registry proposal. Decision packages
also include an offline HTML runner. Open its `index.html` to use it without the
Found-Ry server. Assistant packages contain authored behavior assets for manual
use with a chosen platform; they are not automatically provisioned GPTs.

Generated README instructions describe the exported package. No unrelated
project, entire private registry or local database belongs in a ZIP.

## Privacy and registration

Every draft and package is private. Client overlays, client organization
identities, firewall flags and permanent-private locks activate protection on
save. Established protection and client identity cannot be cleared afterward.
Public graduation remains an explicit maintainer decision outside the app.

The registry view shows local governance records. A draft export produces a
proposal, not a new registry entry or remote GitHub repository. Existing and
retired capability codes remain reserved; an overlay must reference its governed
parent. Enterprise Sleuth variants use aj03 with a unique repository name.
Review the proposal before applying it through the existing governance
process.

## Storage and backup

The default data directory is `.foundry-data/`, ignored by Git. Choose another
private location with `--data-dir /path/to/private-state`. On POSIX systems the app restricts the dedicated data directory to the owner
and sets SQLite state files to owner read/write. This is not encryption;
Windows account access must be managed through operating-system permissions.
The SQLite database
holds original source, project revisions and evaluation records. Protect it as
private content. Stop the application before copying the complete data directory
for backup. Restore that directory and restart with the same `--data-dir`.

The bundled Skillz catalog is a dated public metadata snapshot. It works
offline and does not silently refresh. See [snapshot provenance](../workbench/data/README.md).

## Verification and limits

```bash
python scripts/validate-manifest.py manifest.yaml
python scripts/check-registry.py
python -m unittest discover -s tests -v
```

These checks cover the local runtime and governance contracts. They do not
establish hosted deployment, model quality, external GPT behavior, or Replit
workspace parity. The [research](research/2026-09-07-universe/universe-research.md)
and [execution plan](research/2026-09-07-universe/execution-plan.md) record evidence
and unresolved access limits.

For the public artifact, run `python scripts/build-public-artifact.py --build`.
It checks relative asset references and rejects private/runtime markers before
writing `dist/pages/`. A Pages release is manual and separately reviewed.
