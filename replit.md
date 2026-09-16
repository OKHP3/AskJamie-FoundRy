# AskJamie Found-Ry project overview

Public-source AskJamie capability-building application and governance workbench.
Local drafts and protected exports remain private.
The local application authors assistant specifications, decision tools and
workflows; saves SQLite drafts; records evaluations; and exports governed ZIPs.

## Surface boundary

`public/` is a separately scoped, read-only Pages orientation artifact. It
communicates AskJamie’s relationship to OverKill Hill, Glee-fully, and shared
Skillz, and uses only relative assets. It never reads the local API, SQLite,
`.foundry-data/`, drafts, client records, secrets, or generated packages.

The authoring workbench is a Python standard-library/SQLite application bound to
`127.0.0.1`. It is not hosted in Replit preview or deployment. Public repository
visibility proves source visibility only, not hosted capability operation.
The hosted boundary is documented in
[docs/hosted-authoring-boundary.md](docs/hosted-authoring-boundary.md). Its
provider-independent design was owner-approved on 2026-09-14, but implementation
remains unauthorized. It does not authorize a workflow, hosted database,
authentication connector, provider call, telemetry service, or upload of
`.foundry-data/`, backups, client records, or generated packages.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 -m workbench --port 8765
```

Open http://127.0.0.1:8765. See [operating guide](docs/workbench.md).
The server is loopback-only. Existing Replit project metadata is retained;
its remote workspace, Run behavior and deployment were not verified during
this implementation. Replit preview hosting requires an authenticated access
design and separate parity check, not just binding this private server publicly.

## Ownership

AskJamie is the interpretation region. OverKill is the connective center.
Glee-fully is the personal-tools region. Skillz is shared across all three;
each regional Found-Ry owns its own fabrication line. Historical parent
metadata is provenance. See [ecosystem map](docs/ecosystem-map.md).

## Working contracts

- `AGENTS.md`: canonical agent and governance instructions.
- `workbench/`: Python runtime, static interface and public catalog snapshot.
- `_template/`, `schemas/`, `registry/`: authoritative scaffold/governance assets.
- `tests/`: runtime and validation regression checks.
- `.foundry-data/`: ignored private local state.
- `docs/parity-matrix.md`: evidence-led mentor parity decisions.

Preserve visibility locks, client isolation, lineage, and the locked AutoCAD
R10 constraint. Exports are private packages with pending registry proposals.
No automatic repository creation, publication or graduation occurs.

## Collaboration across agent platforms

Read [AGENTS.md](AGENTS.md) and [the collaboration protocol](docs/agent-collaboration.md).
Continue existing assigned reconciliation work before starting another task.
Share a compact checkpoint through its GitHub issue or PR so ChatGPT/Codex,
Claude, or Copilot can take a bounded part without repeating the whole task.
Replit remains the executor for checks that require its actual workspace.
A GitHub merge alone does not prove this workspace has pulled the change.

## GitHub sync and protected main

Use a task branch and a pull request for source changes. Direct pushes to
`main` are rejected: GitHub requires a PR and the
`Validate with supported Python runtime` check. As a solo-maintainer repository,
it requires zero external approving reviews. Repeating `git pull && git push`
does not satisfy those requirements.

Before changing branches, inspect the working tree, fetch `origin` without
pruning, and record the local and remote commit counts. Preserve pending work.
For a clean checkout ahead of `origin/main`, create a named `codex/` task branch
at the existing commit, push that branch, and open a PR targeting `main`.

Replit's GitHub OAuth connection may reject commits that change
`.github/workflows/` because it lacks `workflow` scope. In that case, preserve
the commits in a Git bundle and transfer it to an already authorized local
checkout. Verify the bundle checksum and source commit, fetch it into a task
branch, then push using that checkout's existing workflow-authorized connection.
Do not copy credentials into Replit, remove workflow files to hide the change,
force-push, or weaken branch protection.

After the PR passes CI, the owner can merge through GitHub.
Fetch again in Replit and verify the intended branch and commit. Use
`git pull --ff-only` only when the histories permit it. If a squash merge leaves
the old Replit commits divergent, retain that branch and coordinate an explicit
switch to a clean branch from `origin/main`; do not reset away pending work.
Pages publication remains a separate, manually approved release.

### Distinguish the three sync failures

- `GH013` on `main`: push a task branch, pass CI, and merge its PR. Zero
  external approvals does not remove the PR requirement.
- `Invalid username or token`: the Shell Git credential is not accepted.
  A connected GitHub integration does not establish that Shell authentication
  works. Refresh the existing Git connection or use the verified bundle route
  above. Do not paste a token into a command, remote URL, or agent message.
- `without workflow scope`: use the existing workflow-authorized Windows
  connection for those commits. Repeating login, pull, or push does not make
  the existing OAuth grant broader.

Use the Shell as the authoritative checkout check. The Git panel can display an
older branch and commit count until refreshed. Start each source task from a
clean, current `main`, then create a named task branch before committing:

```bash
git status --short --branch
git fetch origin
git rev-list --left-right --count HEAD...origin/main
git config --local pull.ff only
# Continue only after preserving pending work and confirming main can fast-forward.
git switch main
git merge --ff-only origin/main
git switch -c task/descriptive-name
# After committing the task's reviewed files:
git push -u origin task/descriptive-name
```

After the PR merges, fetch and fast-forward `main` in both Replit and the
Windows project. Confirm clean status and `0 0` divergence in each. Prefer a
merge commit for recovered Replit history so the original commits remain
ancestors of `main`. Retire resolved task branches and clean temporary worktrees
after verifying their work is merged or preserved in dated archive refs.

The canonical Windows folder is `askjamie-foundry` under the owner's GitHub
mirrors directory. A temporary `askjamie-foundry-sync-*` worktree is an
integration workspace, not another canonical copy. File Explorer reflects the
checked-out files in its selected folder; it does not independently sync Git.
