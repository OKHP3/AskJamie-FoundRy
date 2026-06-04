# archive/

**Role:** Holding area for legacy content staged for graduation to standalone repositories.  
**Status:** Active intake — two efforts currently staged  
**Governed by:** [`AGENTS.md`](../AGENTS.md) — BFS Firewall and visibility rules apply

---

## Purpose

`archive/` preserves original source material that pre-dates the formal
AskJamie capability architecture. Content here is structurally intact, often
valuable, and awaiting the scaffolding work needed to graduate it into its
own governed child repository.

This is **not** a graveyard — it is a staging area. Everything here has a
target repo in [`registry/index.yaml`](../registry/index.yaml).

---

## Staged Capabilities

| Sub-folder | Capability | Code | Family | Target Repo | Status |
|---|---|---|---|---|---|
| [`aj01-resume-representative/`](aj01-resume-representative/README.md) | Résumé Representative | `aj01` | Core Capability | `OKHP3/askjamie-aj01-resume-representative` | Pending graduation |
| [`brg00-builders-firstsource/`](brg00-builders-firstsource/README.md) | BrandGuard — Builders FirstSource | `brg00` | BrandGuard Sentinel | `OKHP3/askjamie-brg00-builders-firstsource` | Pending graduation · 🔒 BFS Firewall |

---

## AJ01 — Résumé Representative

**Folder:** [`aj01-resume-representative/`](aj01-resume-representative/)  
**Original location:** `gpt-aj01-askjamie-resume-representative/` (root, legacy naming)

The original knowledge pack for AskJamie's first capability: dynamic résumé
hybridization, cover letter synthesis, HR intelligence, and compensation
market-value guidance. Developed as a Custom GPT knowledge base and not yet
organized into the formal `skill/`, `prompts/`, `tests/` architecture.

**Contents:** 10 documents across HR guidebooks, hiring analysis, résumé
hybridization methodology, and compensation guidance (PDF, DOCX, Markdown).

---

## BRG00 — Builders FirstSource BrandGuard

**Folder:** [`brg00-builders-firstsource/`](brg00-builders-firstsource/)  
**Original location:** `okhp3-brandguard-sentinel/bfs-framing-intelligent-futures/` (root, legacy naming)

> **⚠️ CONFIDENTIAL — BFS Firewall Active**  
> This content is subject to `bfs_firewall: true` and `visibility_lock: permanent-private`.
> Do not reference, summarize, or share in any public context.

The core GPT instruction set and 18-document knowledge pack for the Builders
FirstSource BrandGuard Sentinel. Covers wood-frame construction, BFS product
catalog, logistics, sustainability, and brand voice.

**Contents:** GPT core instruction (`builders-firstsource-gpt-core.md`),
companion brief, brand narrative, and 18 knowledge documents (PDF + DOCX pairs).

---

## Graduation Process

To graduate a staged capability into its own repo:

1. Create the target repo on GitHub using the naming convention.
2. Copy [`_template/`](../_template/) into the new repo.
3. Organize content from `archive/[code]-[slug]/` into `origin/`, `skill/`, `prompts/`, `knowledge/`.
4. Fill in `manifest.yaml` with correct lineage and visibility settings.
5. Write capability-level `AGENTS.md` and `README.md`.
6. Update `registry/index.yaml` — change `status` from `draft` to `active`.
7. Close the triage entry in `registry/triage.md`.

See [`docs/migration-guide.md`](../docs/migration-guide.md) for full details.

---

## Related

- [`registry/index.yaml`](../registry/index.yaml) — registry entries for both staged capabilities
- [`registry/triage.md`](../registry/triage.md) — resolved triage log
- [`docs/migration-guide.md`](../docs/migration-guide.md) — graduation guide
- [`_template/`](../_template/ABOUT.md) — scaffold to use when creating the target repo
