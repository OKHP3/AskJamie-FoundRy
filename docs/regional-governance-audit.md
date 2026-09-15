# AskJamie regional governance audit

Status: design ready, adoption deferred.

This audit is the gate for adapting broader OverKill Hill governance or
graduation surfaces into AskJamie FoundRy. It does not copy a mentor feature,
change the registry, publish a child repository, or approve public graduation.
It turns a parity proposal into a reviewable record with evidence attached.

## Scope

The audit compares one named OverKill mentor surface with one AskJamie
adaptation. The comparison is regional, not a claim that the two FoundRys have
the same runtime, owner, data, or release state.

The audit covers:

1. the mentor surface and the exact source revision or primary URL reviewed;
2. the proposed AskJamie adaptation and its privacy boundary;
3. registry schema and health validation;
4. protected-client and BFS firewall handling;
5. registry immutability during the audit;
6. evidence classification for every consequential claim;
7. explicit owner approval for the exact adoption scope.

The audit does not cover hosted authoring, model quality, remote child-repository
existence, or public graduation unless those claims receive separate evidence
and approval.

## Evidence tiers

Every consequential claim must have one of these tiers. A tier is a label for
the evidence available, not permission to make a change.

| Tier | Meaning | Minimum record |
|---|---|---|
| `CONFIRMED` | Directly observed in a local file, validator result, tool result, or named primary source | Claim, exact evidence reference, consequence if false, next check |
| `INFERRED` | Reasonable conclusion from confirmed evidence, but not directly observed | Same record, explicitly marked as inferred |
| `PROPOSAL` | Recommended design or adaptation, not an established fact | Rationale, owner, and acceptance condition |
| `UNKNOWN` | Not verified, unavailable, or contradicted by the available evidence | Missing evidence and the check needed to resolve it |

Do not upgrade an `INFERRED`, `PROPOSAL`, or `UNKNOWN` claim because it sounds
plausible or because several agents repeat it. An external mentor claim is
`UNKNOWN` until the named mentor source and revision are reviewed in the audit
record.

## Required audit record

The machine report produced by
`python3 scripts/regional-governance-audit.py` contains:

```yaml
audit:
  name: askjamie-regional-governance
  schema_version: "1.0"
  region: AskJamie
  mentor: OKHP3/OverKill-Hill-FoundRy
  scope: broader-mentor-governance-and-graduation
  mode: design
  status: PASS
  adoption: DEFERRED
evidence:
  - claim: ...
    tier: CONFIRMED
    evidence: [...]
    consequence_if_false: ...
    next_check: ...
registry:
  path: registry/index.yaml
  sha256: ...
  unchanged_during_audit: true
  canonical_validator_errors: []
protected_client_records:
  count: 2
  violations: []
owner_approval:
  required: true
  status: PENDING
```

The report is evidence about the audit run. It is not itself evidence that the
mentor surface is safe to adopt.

## Audit procedure

### 1. Name the surface and freeze the comparison

Record the mentor repository, source revision or URL, the relevant path, and
the AskJamie adaptation being considered. A broad statement such as "adopt
governance" is not an auditable scope. Use a scope such as
`broader-mentor-governance-and-graduation`.

Do not use a registry entry as evidence that a remote repository exists or is
operational. Do not use a Pages response as evidence that authoring,
graduation, or private-state handling is safe.

### 2. Capture the evidence ledger

At minimum, record these claims:

| Claim | Initial tier for this repository | Required resolution |
|---|---|---|
| The AskJamie registry passes the canonical schema and health checks | `CONFIRMED` after the validators run | Keep the validator output with the report |
| Protected client and BFS records remain private and graduation-disabled | `CONFIRMED` after the protected-record sweep | Keep the record count and any violations |
| The registry did not change during the audit | `CONFIRMED` when the before/after digest matches | Preserve the SHA-256 digest |
| The mentor surface has the stated governance or graduation behavior | `UNKNOWN` until the named mentor source is reviewed | Add source revision, path, observation, and reviewer |
| The proposed AskJamie adaptation is safe for the regional boundary | `PROPOSAL` or `UNKNOWN` | Review privacy, ownership, and acceptance proof |
| Adoption is authorized | `UNKNOWN` until the owner signs the exact scope | Record owner, date, scope, and digest |

The current parity matrix establishes the first three kinds of local boundary
evidence. It intentionally does not establish the last three.

### 3. Run local controls without mutation

Run:

```bash
python3 scripts/validate-manifest.py manifest.yaml
python3 scripts/check-registry.py
python3 scripts/registry-audit.py
python3 scripts/regional-governance-audit.py
```

The regional audit reads the registry, invokes the canonical registry
validator, counts protected records, and compares the registry digest before
and after the checks. It must not write `registry/index.yaml` or any child
record. A supplied baseline digest must match exactly.

If a validator fails, the audit is a failure. Do not repair the registry
inside the audit run and then report a clean result.

### 4. Apply protected-client handling

Treat any entry with `family: client-overlay`, `client_org`,
`bfs_firewall: true`, or `visibility_lock: permanent-private` as protected.
Every protected entry must have:

```yaml
visibility: private
public_graduation_allowed: false
visibility_lock: permanent-private
```

Client names and client-specific source are not copied into a public report.
The report may include a count and neutral violation identifiers, but not
client content. BFS firewall material is not summarized, linked, or mixed into
the public orientation artifact.

### 5. Require owner approval

Owner approval is required for adoption, not merely for running the audit. The
approval record must be separate from the audit output and must include:

```yaml
audit: askjamie-regional-governance
scope: broader-mentor-governance-and-graduation
decision: approve
owner: OKHP3
approved_at: "YYYY-MM-DD"
registry_sha256: "<digest from the reviewed report>"
```

Approval applies only to the named scope and digest. It does not authorize
hosted authoring, model calls, child-repository creation, public graduation,
or a different registry state. If any required claim remains `UNKNOWN`, the
adoption decision remains `DEFERRED` even when an owner has approved the
design to continue review.

## Decision gate

| Condition | Result |
|---|---|
| Local validator error, protected-record violation, or digest mismatch | `FAIL`, stop |
| Mentor source, regional adaptation, or owner decision is unverified | `PASS` audit run, `DEFERRED` adoption |
| All required claims are `CONFIRMED`, protections pass, digest matches, and owner approval matches the scope | Eligible for a separate implementation decision |
| Any public graduation or client visibility change is proposed | Stop and open a separate owner-approved graduation review |

The normal result for this repository is currently `PASS` for local controls and
`DEFERRED` for broader mentor governance adoption. That is the intended safe
state until the mentor comparison and owner decision are recorded.

## Remaining unknowns

- Which exact OverKill governance and graduation surfaces should be compared
  first.
- Whether their current behavior is still present at a reviewed mentor revision.
- Which parts are useful to AskJamie without changing its Python loopback,
  private-export, and permanent-private boundaries.
- Whether the owner approves a specific adaptation after those claims are
  confirmed.

The next check is a named mentor-source review followed by an owner decision
against the resulting evidence ledger. Until then, keep the parity decision at
`defer`.