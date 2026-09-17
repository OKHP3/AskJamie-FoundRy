# AskJamie regional governance audit

Status: design ready, owner decision recorded as defer, adoption deferred.

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
7. explicit owner decision for the exact adaptation and adoption scope.

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

## Named mentor-surface review

The first reviewed surface is the OverKill public-graduation audit. This is a
review of one pinned source revision, not a claim about every current mentor
workflow or permission.

| Field | Evidence |
|---|---|
| Repository revision | `OKHP3/OverKill-Hill-FoundRy@8de1eb212d8db193fd22eb85bf0843f366a0c1a7` |
| Primary source URL | [`scripts/public-graduation-audit.py`](https://github.com/OKHP3/OverKill-Hill-FoundRy/blob/8de1eb212d8db193fd22eb85bf0843f366a0c1a7/scripts/public-graduation-audit.py) |
| Path | `scripts/public-graduation-audit.py` |
| Observation | The read-only dry-run checks release-package completeness, restricted references, record consistency, and manual disabled deployment; it does not grant publication approval or change repository visibility. |
| Reviewed | 2026-09-17 |
| Reviewer | Replit Agent |

The observation is `CONFIRMED` for this exact revision and path. It does not
confirm that a later mentor revision behaves the same way, that the target
package is safe for AskJamie, or that any publication approval exists.

## Exact AskJamie adaptation

The named adaptation under review is deliberately narrow:

| Field | Record |
|---|---|
| Adaptation ID | `read-only-regional-mentor-governance-audit` |
| Adaptation | Use the pinned mentor audit as evidence for a private AskJamie governance review. Do not copy a governance or graduation surface. |
| Regional boundary | Keep the Python loopback workbench, private exports, permanent-private client controls, and immutable registry unchanged. |
| Publication decision | `not-authorized` |
| Hosting decision | `not-authorized` |

This is an evidence and review adaptation, not adoption of a mentor governance
or graduation surface. The owner decision is recorded in
[`regional-governance-decision.yaml`](regional-governance-decision.yaml) and
is bound to the registry digest in that file.

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
adaptation:
  id: read-only-regional-mentor-governance-audit
  publication_decision: not-authorized
  hosting_decision: not-authorized
evidence:
  - claim: ...
    tier: CONFIRMED
    evidence: [...]
    consequence_if_false: ...
    next_check: ...
mentor_review:
  repository: OKHP3/OverKill-Hill-FoundRy
  revision: 8de1eb212d8db193fd22eb85bf0843f366a0c1a7
  path: scripts/public-graduation-audit.py
  reviewed_at: "2026-09-17"
  reviewer: Replit Agent
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
  status: DEFERRED
  decision: defer
  decided_at: "2026-09-17"
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
| The mentor surface has the stated governance or graduation behavior | `CONFIRMED` for the pinned revision and path reviewed above; `UNKNOWN` for unreviewed revisions or surfaces | Retain the source revision, path, observation, and reviewer |
| The proposed AskJamie adaptation is safe for the regional boundary | `PROPOSAL` or `UNKNOWN` | Review privacy, ownership, and acceptance proof |
| The owner has decided the exact adaptation | `CONFIRMED` after the decision record matches the adaptation, scope, date, digest, publication boundary, and hosting boundary | Keep `docs/regional-governance-decision.yaml` with the reviewed digest |

The current parity matrix establishes the first three kinds of local boundary
evidence, and the named mentor review above establishes the observed behavior
of one pinned surface. It intentionally does not establish that the proposed
AskJamie adaptation is safe or that adoption is authorized.

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

### 5. Record the owner decision

An owner decision is required for adoption, not merely for running the audit. The
decision record must be separate from the audit output and must include:

```yaml
audit: askjamie-regional-governance
scope: broader-mentor-governance-and-graduation
adaptation: read-only-regional-mentor-governance-audit
decision: defer
owner: OKHP3
decided_at: "YYYY-MM-DD"
registry_sha256: "<digest from the reviewed report>"
publication_decision: not-authorized
hosting_decision: not-authorized
```

`decision` must be `approve`, `defer`, or `reject`. The record applies only to
the named adaptation, scope, registry digest, publication boundary, and hosting
boundary. It cannot be reused for a different registry state, a publication
release, or a hosting decision. An approval also does not authorize hosted
authoring, model calls, child-repository creation, or public graduation.

The current record is `defer` because the regional adaptation remains a
proposal. Run the audit with the record to verify the exact binding:

```bash
python3 scripts/regional-governance-audit.py \
  --owner-approval docs/regional-governance-decision.yaml \
  --require-approval
```

The `--require-approval` flag means a matching record exists. It does not turn
the deferred adaptation into an approved publication or hosting decision.

## Decision gate

| Condition | Result |
|---|---|
| Local validator error, protected-record violation, or digest mismatch | `FAIL`, stop |
| Mentor source, regional adaptation, or owner decision is unverified | `PASS` audit run, `DEFERRED` adoption |
| All required claims are `CONFIRMED`, protections pass, digest matches, and an approving decision matches the exact scope and boundaries | Eligible for a separate implementation decision |
| Any public graduation or client visibility change is proposed | Stop and open a separate owner-approved graduation review |

The normal result for this repository is currently `PASS` for local controls and
`DEFERRED` for broader mentor governance adoption. The owner decision is
recorded as `defer`, so no broader mentor governance or graduation surface is
adopted.

## Remaining unknowns

- Which exact OverKill governance and graduation surfaces should be compared
  next; this audit covers only `scripts/public-graduation-audit.py`.
- Whether the reviewed behavior remains present in a later mentor revision.
- Which parts are useful to AskJamie without changing its Python loopback,
  private-export, and permanent-private boundaries.
- Whether the owner should revisit the deferred adaptation after the regional
  boundary review is complete.

The next check is a regional boundary review against the named adaptation. Until
that review is complete, keep the parity decision at `defer` and do not reuse
the decision record for publication or hosting.