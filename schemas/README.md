# schemas/

**Role:** Canonical YAML schema definitions for manifest and registry validation.  
**Owner:** OKHP3/AskJamie-FoundRy (this relay owns these schemas)  
**Rule:** Any breaking change to a schema must increment `schema_version` and be
documented in `CHANGELOG.md`.

---

## Contents

| File | Validates | Used By |
|---|---|---|
| [`manifest.schema.yaml`](manifest.schema.yaml) | `manifest.yaml` in every child repo | `scripts/validate-manifest.py` |
| [`registry.schema.yaml`](registry.schema.yaml) | `registry/index.yaml` | `scripts/check-registry.py` |

---

## `manifest.schema.yaml`

Defines the required and optional fields for any `manifest.yaml` governed by
this relay. Required top-level keys:

```
schema_version · identity · brand · lineage · governance
visibility_control · maintainers · created · updated
```

Key constraints:
- `identity.repo` must match `^OKHP3/.+`
- `identity.type` must be one of: `core-capability`, `brandguard`,
  `enterprise-sleuth`, `client-overlay`, `conversation-design`, `rag-experiment`
- `identity.status` must be one of: `draft`, `active`, `deprecated`
- `visibility_control.visibility` must be `private` or `public`

### Validate a Manifest

```bash
python3 scripts/validate-manifest.py path/to/manifest.yaml

# Examples:
python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/validate-manifest.py ../askjamie-aj01-resume-representative/manifest.yaml
```

---

## `registry.schema.yaml`

Defines the required structure for `registry/index.yaml` entries. Each entry
in the `repositories` list must declare:

```
repo · display_name · code · family · status · visibility · description
```

Client overlay entries additionally require:
```
client_org · visibility_lock · public_graduation_allowed: false
```

### Validate the Registry

```bash
python3 scripts/check-registry.py
```

---

## Updating a Schema

1. Edit the relevant `*.schema.yaml` file.
2. If the change adds or removes a **required** field, increment `schema_version`
   in the schema and in all manifests/registry files that use it.
3. Update `_template/manifest.yaml` to include any new required fields.
4. Run both validation scripts to confirm no regressions:

```bash
python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/check-registry.py
```

5. Document the change in `CHANGELOG.md`.

---

## Related

- [`scripts/validate-manifest.py`](../scripts/validate-manifest.py) — manifest validator
- [`scripts/check-registry.py`](../scripts/check-registry.py) — registry health check
- [`_template/manifest.yaml`](../_template/manifest.yaml) — reference implementation
- [`manifest.yaml`](../manifest.yaml) — this FoundRy's own manifest (validates against this schema)
- [`docs/governance.md`](../docs/governance.md) — schema ownership rules
