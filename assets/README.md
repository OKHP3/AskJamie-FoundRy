# assets/

**Role:** Shared brand and media assets for the AskJamie FoundRy and its child repositories.  
**Owner:** OKHP3/AskJamie-FoundRy

---

## Structure

```
assets/
└── brand/          AskJamie™ brand standards and identity assets
```

---

## brand/

**→ See [`brand/README.md`](brand/README.md) for full details.**

Contains the canonical AskJamie™ Brand Standards documents — the authoritative
reference for logo usage, typography, color palette, tone of voice, and identity
guidelines across all deployment surfaces.

| File | Description |
|---|---|
| [`brand/askjamie-brand-standards.pdf`](brand/askjamie-brand-standards.pdf) | Brand Standards (PDF, print-ready) |
| [`brand/askjamie-brand-standards.docx`](brand/askjamie-brand-standards.docx) | Brand Standards (DOCX, editable source) |

---

## Usage Rules

- **Reference, don't copy.** Child repos should reference assets from this
  location rather than duplicating them.
- **Version on change.** If a brand standards file is updated, append a version
  suffix to the filename (e.g., `askjamie-brand-standards-v2.pdf`) and keep the
  previous version for a grace period.
- **No client content here.** Assets specific to a BrandGuard Sentinel or
  client overlay belong in that capability's own `assets/` directory, not here.

---

## Adding New Asset Types

If the FoundRy grows to include additional shared assets (icons, illustration
kits, video intros, font files), create a new named subfolder under `assets/`
and add a `README.md` for it. Update this file's structure table.

---

## Related

- [`assets/brand/README.md`](brand/README.md) — brand subfolder documentation
- [`docs/naming-conventions.md`](../docs/naming-conventions.md) — file naming rules
