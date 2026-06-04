# registry/

**Role:** Authoritative catalog and intake log for all child repositories governed by this relay.  
**Owner:** OKHP3/AskJamie-FoundRy  
**Rule:** The registry is the source of truth. A repo not in `index.yaml` is not formally governed.

---

## Contents

| File | Purpose |
|---|---|
| [`index.yaml`](index.yaml) | Master registry of all governed child repositories |
| [`triage.md`](triage.md) | Intake and decision log for candidate repos and content |

---

## `index.yaml` — The Registry

The authoritative list of every repository in the AskJamie ecosystem. Each entry
declares the repo's identity, capability code, family, status, visibility, and
any client/firewall flags.

### Currently Registered Repos (9)

| Repo | Code | Family | Status | Visibility |
|---|---|---|---|---|
| `askjamie-aj01-resume-representative` | `aj01` | core-capability | active | private |
| `askjamie-aj02-professional-portfolio` | `aj02` | core-capability | draft | private |
| `askjamie-aj03-enterprise-sleuth` | `aj03` | enterprise-sleuth | draft | private |
| `askjamie-aj04-brandguard` | `aj04` | brandguard | draft | private |
| `askjamie-brg00-builders-firstsource` | `brg00` | brandguard | active | private 🔒 |
| `askjamie-brg01-lego` | `brg01` | brandguard | draft | private 🔒 |
| `askjamie-brg12-mathews-archery` | `brg12` | brandguard | draft | private 🔒 |
| `buildersfirstsource-askjamie-aj03-enterprise-sleuth` | `aj03` | client-overlay | draft | private 🔒 |
| `cvshealth-askjamie-aj03-enterprise-sleuth` | `aj03` | client-overlay | draft | private 🔒 |

🔒 = `visibility_lock: permanent-private` — public graduation not allowed

### Status Values

| Value | Meaning |
|---|---|
| `draft` | Planned or in-progress — repo may not exist on GitHub yet |
| `active` | Governed and operational |
| `deprecated` | No longer maintained; preserved for lineage |
| `archived` | Formally decommissioned |

### Adding a New Entry

1. Determine the capability code (`aj##` or `brg##`) and family.
2. Add a YAML block following the existing pattern in `index.yaml`.
3. Set `status: draft` until the repo is created and scaffolded.
4. Run the registry health check:

```bash
python3 scripts/check-registry.py
```

---

## `triage.md` — The Intake Log

Used to track candidate content or repos that are being evaluated before formal
registration. Once a decision is made, move the entry to `index.yaml` and close
the triage record.

**Active triage:** None currently.  
**Resolved entries:** AJ01 and BRG00 (legacy folders — both archived).

---

## Registry Health Check

```bash
python3 scripts/check-registry.py
```

Validates that `index.yaml` conforms to `schemas/registry.schema.yaml` and
reports status summaries, public graduation candidates, and permanent-private repos.

---

## Related

- [`schemas/registry.schema.yaml`](../schemas/registry.schema.yaml) — schema for this file
- [`scripts/check-registry.py`](../scripts/check-registry.py) — health check script
- [`registry/triage.md`](triage.md) — intake log
- [`docs/governance.md`](../docs/governance.md) — registry maintenance obligations
