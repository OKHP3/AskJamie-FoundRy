# Naming Conventions — AskJamie FoundRy

## Canonical Patterns

### Core Capability Repositories

```
askjamie-aj##-[capability-slug]
```

- `##` = zero-padded two-digit numeric code (01–99)
- `[capability-slug]` = lowercase, hyphen-separated, descriptive slug
- Examples:
  - `askjamie-aj01-resume-representative`
  - `askjamie-aj02-professional-portfolio`
  - `askjamie-aj03-enterprise-sleuth`
  - `askjamie-aj04-brandguard`

### BrandGuard Sentinel Repositories

```
askjamie-brg##-[brand-slug]
```

- `##` = zero-padded two-digit numeric code (00–99)
- `[brand-slug]` = lowercase, hyphen-separated brand name
- Examples:
  - `askjamie-brg00-builders-firstsource`
  - `askjamie-brg01-lego`
  - `askjamie-brg12-mathews-archery`

### Client Overlay Repositories

```
[client-org]-askjamie-[capability-code]-[capability-slug]
```

- `[client-org]` = lowercase org slug (e.g., `buildersfirstsource`, `cvshealth`)
- `[capability-code]` = the code of the parent capability (e.g., `aj03`)
- `[capability-slug]` = the slug of the parent capability
- Examples:
  - `buildersfirstsource-askjamie-aj03-enterprise-sleuth`
  - `cvshealth-askjamie-aj03-enterprise-sleuth`

---

## Code Assignment Rules

### `aj##` Codes

| Code | Assigned To |
|---|---|
| `aj01` | Résumé Representative |
| `aj02` | Professional Portfolio |
| `aj03` | Enterprise Sleuth |
| `aj04` | BrandGuard (core) |
| `aj05`–`aj99` | Reserved / future assignment |

New `aj` codes are assigned sequentially. Never reuse a retired code.

### `brg##` Codes

| Code | Assigned To |
|---|---|
| `brg00` | Builders FirstSource |
| `brg01` | LEGO (planned) |
| `brg02`–`brg11` | Reserved / future assignment |
| `brg12` | Mathews Archery (planned) |

New `brg` codes are assigned sequentially. Never reuse a retired code.

---

## Slug Rules

- All lowercase.
- Hyphens only — no underscores, no spaces, no special characters.
- Descriptive but concise — aim for 1–3 words.
- Must be stable once assigned; renaming a live repo breaks lineage.

Good: `resume-representative`, `enterprise-sleuth`, `builders-firstsource`
Bad: `resumeRep`, `ent_sleuth`, `BFS GPT`, `builders_firstsource`

---

## Manifest Slug vs. Repo Slug

The `manifest.yaml` `slug` field must match the slug portion of the repo name:

```yaml
identity:
  repo: OKHP3/askjamie-aj01-resume-representative
  slug: resume-representative
```

---

## Legacy / Non-Standard Names (Do Not Use)

These naming patterns existed before the current standard was adopted.
Their former local content has been removed, and they must not be used for new repos:

| Legacy Name | Standard Equivalent |
|---|---|
| `gpt-aj01-askjamie™-—-résumé-representative` | `askjamie-aj01-resume-representative` |
| `OKHP3-BrandGaurd-Sentinel/BFS-Framing-Intelligent-Futures` | `askjamie-brg00-builders-firstsource` |

---

## GitHub Repository Settings

When creating a new child repo, apply these standard GitHub settings:

- **Visibility:** Private (always start private)
- **Default branch:** `main`
- **Description:** Match the `display_name` from `manifest.yaml`
- **Topics/Labels:** Include `askjamie`, the capability code, and the family
  (e.g., `brandguard`, `core-capability`)
- **Homepage URL:** `https://askjamie.bot/` for public-candidate repos
- **Wikis:** Disabled (use `docs/` instead)
- **Issues:** Enabled
- **Projects:** Optional

---

## Replit Project Naming

Replit projects paired with AskJamie repos follow this pattern:

```
[DisplayName] (no code prefix needed in Replit, spaces allowed)
```

Example: `AskJamie — Résumé Representative` or `AskJamie Résumé Representative`
