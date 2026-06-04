# GitHub Workflows — Staged

These workflow files are staged here because the GitHub OAuth token used by
Replit does not have the `workflow` scope required to push directly to
`.github/workflows/`.

The files are production-ready. Once you have a token with `workflow` scope,
activate them by running:

```bash
cp docs/github-workflows/validate-manifests.yml .github/workflows/validate-manifests.yml
cp docs/github-workflows/registry-lint.yml .github/workflows/registry-lint.yml
git add .github/workflows/
git commit -m "ci: activate GitHub Actions workflows"
git push
```

## Workflows in This Directory

| File | Triggers | Purpose |
|---|---|---|
| `validate-manifests.yml` | PR or push touching any `manifest.yaml` or `schemas/manifest.schema.yaml` | Validates all `manifest.yaml` files against the schema |
| `registry-lint.yml` | PR or push touching `registry/index.yaml` or `schemas/registry.schema.yaml` | Runs registry health check |

## How to Get `workflow` Scope

**Option A — Personal Access Token (classic):**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → check `workflow` scope
3. In Replit: use this token when authenticating GitHub pushes

**Option B — Fine-grained PAT:**
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Repository access → select `AskJamie-FoundRy`
3. Permissions → Actions: Read & write

**Option C — GitHub web editor:**
After the rest of the repo is pushed, create each workflow directly in the
GitHub web UI (`.github/workflows/` → Add file → Create new file → paste content).
GitHub's own web editor bypasses the OAuth scope restriction.
