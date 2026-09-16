# Hosted authoring boundary design

**Status:** design approved by owner on 2026-09-14; implementation not authorized
**Applies to:** a possible future multi-device or multi-user AskJamie authoring
runtime
**Current decision:** keep authoring loopback-only. This design approval does
not authorize hosting, a provider integration, or moving existing drafts
online. Those actions remain prohibited until a separate implementation task is
authorized and its acceptance evidence exists.

This document defines the minimum boundary for a future hosted authoring
service. It is not a hosting plan, an authorization to deploy, or evidence that
the current workbench is safe to expose. The current implementation remains the
Python standard-library/SQLite service bound to `127.0.0.1`, as defined by the
[workbench contract](workbench-contract.md).

## 1. Non-negotiable invariants

The hosted design must preserve these existing decisions:

1. `public/` remains a static, read-only orientation artifact. It cannot call
   an authoring API, read a database, inspect browser storage, or receive
   generated packages.
2. Drafts, source text, evidence, evaluations, client identities, revision
   history, backups, and generated ZIPs are private by default.
3. Client overlays, `client_org`, `bfs_firewall`, and
   `visibility_lock: permanent-private` are permanent privacy controls. A
   hosted service must not provide an operation that clears or weakens them.
4. The server remains the authority for identity, workspace membership,
   visibility, revision checks, export readiness, and package contents.
   Browser fields and URL values are never authorization input.
5. No model-provider call, skill execution, arbitrary code execution,
   automatic repository creation, public graduation, or package publication is
   implied by hosted authoring.
6. The loopback mode remains supported. A hosted mode must not require an owner
   to upload the existing `.foundry-data/` directory or private backups just to
   continue local work.

## 2. Trust zones and data classes

| Zone | Allowed content | Forbidden content |
|---|---|---|
| Public Pages artifact | Curated public relationship, governance, and orientation text; relative static assets | API responses, SQLite files, drafts, client records, backups, ZIPs, secrets, browser storage |
| Hosted edge and application | Authenticated requests, validated project commands, short-lived request context | Direct browser-to-database access, provider credentials in the browser, unbounded uploads, raw private data in logs |
| Tenant data store | Records assigned to one workspace, including revisions and evaluations | Rows without a workspace owner, cross-tenant search results, public indexes |
| Private package/backup vault | Encrypted project exports and recovery backups with an owner and retention label | Public URLs, anonymous downloads, untracked copies, credentials or session tokens |
| Optional future provider adapter | Only explicitly approved, minimum necessary, redacted content for a named operation | Automatic source upload, training use, client data by default, provider calls from the current local runtime |

The sensitive data class includes more than the SQLite file itself. It includes
the source text, provenance claims, evidence, evaluation inputs and responses,
client organization identifiers, revision history, generated package contents,
backup envelopes, download URLs, request bodies, and error details that could
reconstruct any of those values.

## 3. Authentication and authorization design

### Authentication requirements

Before hosting is considered, the selected runtime must provide:

- OIDC or an equivalent standards-based identity provider with authorization
  code plus PKCE. The application must not collect or store provider
  passwords.
- A maintained owner allowlist for the first release. New users require an
  explicit owner action; account discovery and open self-registration are
  disabled.
- MFA enforced by the identity provider for owner and administrator accounts.
- A server-side identity mapping keyed by `(issuer, subject)`, not by email
  alone. Email changes must not silently transfer ownership.
- Short-lived, rotated sessions in `Secure`, `HttpOnly`, `SameSite` cookies.
  Logout, session revocation, idle expiry, and reauthentication for export,
  restore, membership, and destructive actions are required.
- CSRF protection for every cookie-authenticated state-changing request.
  CORS is deny-by-default and is not a substitute for CSRF protection.

The hosted application must never put an access token, session secret,
encryption key, provider key, or backup credential in HTML, JavaScript,
downloaded packages, URLs, analytics, or exception responses.

### Authorization requirements

Authorization is deny-by-default and evaluated on every request:

- A workspace is the security boundary. Every project, revision, evaluation,
  package, backup, and audit event carries a server-assigned workspace ID.
- The first release has explicit roles: owner, editor, reviewer, and exporter.
  Restore, membership changes, client-workspace deletion, and policy changes
  require owner approval. A reviewer cannot edit or export unless separately
  granted that permission.
- Client workspaces are isolated from the owner’s general portfolio workspace.
  There is no global client search, cross-client dashboard, or support access
  that bypasses the workspace policy.
- IDs are unguessable, but authorization does not depend on that property.
  Every object lookup applies the authenticated workspace scope before
  returning a result. Missing and unauthorized objects use the same safe
  response shape.
- Visibility and graduation flags are server-controlled. Public Pages never
  consumes hosted records, and a hosted record cannot become public through a
  normal save or export action.

## 4. Data routing and storage

The only permitted hosted request path is:

```text
browser
  -> TLS termination with security headers
  -> authenticated application boundary
  -> authorization and input validation
  -> tenant-scoped application service
  -> tenant-scoped database or private object vault
```

Required routing rules:

1. The browser sends project commands to the application API over TLS. It never
   connects directly to SQLite, a database proxy, an object bucket, or a
   provider API.
2. The application derives `workspace_id`, actor, role, and privacy controls
   from the authenticated session. Client-supplied copies of those values are
   ignored or rejected.
3. Each query, write, export, backup, and restore operation applies workspace
   scope in the service layer and, where supported, a database row-level
   policy. Tests must prove both paths, not only the UI path.
4. SQLite is not placed in a public directory, mounted into a static artifact,
   or made available through a download route. If a hosted database is chosen,
   it must be a managed private data service with encryption in transit and at
   rest, access logging, backups, and a documented restore procedure.
5. Generated ZIPs and backup envelopes are private objects with separate
   authorization checks. Downloads use short-lived, single-purpose URLs or a
   streamed response after an authorization check. They are not indexed,
   cached publicly, or placed in the Pages artifact.
6. Logs, metrics, traces, crash reports, search indexes, and support snapshots
   receive structured redaction before collection. Request bodies, source text,
   client names, package contents, cookies, authorization headers, and backup
   data are excluded by default.
7. The hosted service has egress controls. No outbound provider or arbitrary
   URL request is permitted in the first hosted authoring release.

## 5. Client-record handling

Client records are a separate privacy class, not merely another project
field.

- A client workspace is created only by an owner action with a recorded
  purpose, owner, retention class, and membership list.
- `client_org` is a sensitive workspace attribute. It is not a public slug,
  URL path, registry label, search result, page title, telemetry value, or
  generated public metadata field.
- Client source, evidence, evaluations, history, and packages remain inside
  that workspace. The service must reject copying them into the public
  portfolio workspace or `public/`.
- Client records are not used for model training, product analytics, skill
  refresh, mentor comparison, or cross-client recommendations. The first
  hosted release makes no model, inference, external-data, or arbitrary-URL
  provider call.
- Export is an explicit, audited action. A package retains its private
  manifest controls and provenance, contains only the selected project, and
  cannot be published by the service. A client package must carry a private
  retention label and an owner-visible audit event.
- Deletion requires owner confirmation, an export/retention decision, and a
  recorded completion result. Legal or contractual holds pause deletion.
  Deletion must cover active rows, revisions, evaluations, object copies,
  indexes, short-lived download objects, and expired backup copies according
  to the selected provider’s documented deletion guarantees.

## 6. Backup and retention design

The following owner-approved schedule is the provider-independent minimum for a
future hosted service. It is not a claim about the current local backup behavior
or evidence that any provider can meet it.

| Item | Required handling | Approved retention |
|---|---|---|
| Database backup | Encrypted, workspace-aware backup; encryption keys are separate from the data service; access is owner-only | Daily snapshots for 35 days |
| Recovery points | Immutable copy before destructive migration, restore, or deletion; tagged with actor and reason | 35 days unless a hold applies |
| Long-term recovery | Encrypted weekly restore point with a tested manifest and checksum | 12 weeks |
| Release or governance hold | Explicit owner-created hold with expiry or review date | Until the hold is released |
| Generated ZIP | Encrypted private object, no public cache, no anonymous link | 7 days by default, then delete |
| Audit record | Keep action, actor, workspace, object class, result, and timestamp; do not store source content | 12 months, subject to owner policy |

The schedule applies by data class as follows:

| Data class | Normal lifecycle and deletion scope |
|---|---|
| Active project data | Retained while the workspace is active. An approved workspace or project deletion removes the active rows and tenant-scoped metadata. |
| Revisions and evaluations | Follow the owning project. They are deleted with it and cannot be retained as detached history. |
| Object copies | Temporary render, staging, quarantine, support, and migration copies inherit the source object's retention label and must be included in deletion reports. Untracked copies are prohibited. |
| Download objects and generated ZIPs | Expire after 7 days by default. Revocation blocks retrieval immediately; physical provider deletion follows the provider's documented deletion window. A user-downloaded copy is outside service control and the interface must say so before download. |
| Backups and recovery points | Age out on the 35-day or 12-week schedule above. A logical deletion prevents ordinary restore of the deleted workspace; physical backup copies expire under the schedule unless a hold applies. |
| Search indexes, caches, and derived metadata | Contain no source text by default and are purged or rebuilt without the deleted workspace as part of the deletion operation. |
| Audit records | Content-free records remain for 12 months, then expire. They may retain the fact and result of a deletion, but not deleted source, package contents, client names, or reconstructable payloads. |

### Holds, deletion, and key control

- Only an owner may create, extend, or release a legal, contractual, release, or
  governance hold. Every hold names its scope, reason, creator, creation time,
  review or expiry date, and release result.
- A hold pauses physical deletion only for the named objects and their required
  recovery copies. It does not make them downloadable, widen membership, permit
  public use, or suspend access controls. Expired holds require owner review;
  they do not silently become permanent.
- A deletion request first revokes sessions and download access, then removes
  active data, revisions, evaluations, object copies, indexes, caches, and
  derived metadata. Backup expiry and provider-side physical deletion are
  tracked separately. The service reports `deletion pending` until every
  in-scope provider copy is evidenced as deleted or an active hold is recorded.
- Encryption keys must be owner-controlled and separate from the data service.
  The selected provider may operate the key service, but must support
  owner-authorized rotation, revocation, access logs, and cryptographic erasure
  for workspace- or vault-scoped keys. Provider-managed-only keys are not
  acceptable.
- A selected host must contractually document deletion behavior for primary
  storage, replicas, object versions, caches, indexes, logs, snapshots, and
  disaster-recovery copies; the maximum deletion window after retention expiry;
  hold handling; subprocessors; and evidence available on completion. If any
  class cannot meet this policy, private drafts cannot move to that provider.
- Deletion evidence must identify the workspace, object classes, request and
  completion times, held exceptions, provider operation or report identifiers,
  and the actor who verified completion. It must not contain private payloads.

Backups must not be treated as a second public export path. Restore is performed
into an isolated, access-controlled environment first. A restore is not complete
until schema validation, checksum verification, workspace-isolation tests, and
public-route checks pass. Retention jobs must report failures and must not
silently claim deletion when a provider copy remains.

### Restore and deletion verification runbook

1. Record the owner-approved restore purpose, workspace scope, recovery point,
   operator, and expected checksum. Reject expired, foreign-workspace, unlabelled,
   or held-for-an-incompatible-purpose recovery points.
2. Restore into a disposable isolated environment with public routes, outbound
   egress, ordinary users, and package downloads disabled. Never restore over
   active production data.
3. Verify the manifest, checksum, schema, revision continuity, evaluation
   references, privacy flags, object ownership, and retention labels before
   enabling application reads.
4. Run the provider adapter acceptance harness against the restored environment,
   including same-workspace positive controls, cross-workspace denials, public
   route scans, expired-link denial, and private cache/index inspection.
5. Reconcile restored object counts and identifiers to the approved workspace
   scope. Any commingled, missing, or unlabelled object fails the restore.
6. Record the result without private content. Promote data only through a
   separately approved recovery action; otherwise destroy the isolated restore
   and obtain provider evidence for its database, object, cache, index, log,
   snapshot, and key copies.
7. Keep the result as `restore cleanup pending` or `deletion pending` until the
   provider's documented evidence confirms completion. A successful application
   delete, inaccessible URL, empty query, retention-job request, or key-revocation
   request is not by itself evidence of physical deletion.

The owner has approved the retention periods, deletion requirements, key
ownership model, 24-hour recovery point objective, and 72-hour recovery time
objective above. Provider selection, data location, disaster-recovery region,
and proof that the provider satisfies these guarantees remain deployment-specific
gates and cannot be inferred from the local SQLite implementation.

## 7. Leak-prevention proof

Hosted authoring is not approved until the following evidence is attached to the
implementation review. A passing unit test alone is insufficient.

| Claim to prove | Required evidence |
|---|---|
| Public artifact cannot reach authoring state | Clean build of `public/` and `dist/pages/`; route and network inspection shows no API, database, object-vault, or browser-storage dependency; static scan finds no SQLite, backup, draft, client, secret, or generated-package content |
| SQLite and private state cannot be served | Route inventory and negative tests show no database path, data-directory path, directory listing, backup route, or package route under the public artifact or unauthenticated edge |
| A user cannot cross workspace boundaries | Two-workspace fixture with read, write, history, evaluate, export, backup, restore, duplicate, and delete attempts using valid IDs from the other workspace; every attempt is denied without content disclosure |
| Client records stay private | Client-workspace fixture, public artifact scan, export inspection, log inspection, and deletion/retention report show no client data outside the authorized workspace and private vault |
| Generated packages are contained | Every ZIP is unpacked in a clean directory and checked for only the selected project, approved metadata, no database, no other project, no credentials, no backup, no registry dump, and preserved permanent-private flags |
| Backups cannot become downloads | Backup authorization, object ACL, cache-header, expiry, restore-isolation, and retention-deletion evidence are recorded; an expired or revoked link cannot retrieve data |
| No model, external-data, or arbitrary egress occurs | Dependency/import inventory, deny-by-default egress policy, request audit, and tests prove that the first hosted authoring release makes no model, inference, external-data, or arbitrary URL call |
| Errors and telemetry do not leak content | Deliberately hostile requests and failed exports/restores are inspected in logs, traces, metrics, browser output, and support artifacts for source, client, token, package, and backup values |
| Recovery does not widen access | Restore a multi-workspace fixture into an isolated environment, rerun authorization and public-route checks, and compare privacy flags and workspace ownership before and after |

The existing local proof remains relevant but is narrower: the manifest marks
the private workbench as loopback-only, the contract limits writes and export
contents, the public build rejects private/runtime markers, and the local
boundary and export tests cover host/origin controls and package isolation.
Those checks do not prove network authentication, hosted authorization,
encryption, object ACLs, retention, or provider egress.

### Provider-independent acceptance harness

`tests/hosted_isolation_harness.py` defines the adapter contract that a future
hosted implementation must satisfy. `tests/test_hosted_isolation_proof.py`
runs that contract against a deterministic two-workspace reference adapter and
produces a JSON-serializable evidence report. It covers foreign valid-ID
attempts and same-path positive controls for read, write, history, evaluate,
export, backup, restore, duplicate, and delete using session-mapped principals;
package and logical-backup inspection; isolated restore; expired and
foreign backup denial; same-path authorization checks for every operation after
restore; expired download denial; empty private caches; redacted audit evidence;
and scans of both `public/` and `dist/pages/`.

Run `python3 scripts/prove-hosted-isolation.py` from the repository root to
print the current certification status as JSON. While no provider is selected,
the report distinguishes a passing local reference contract from a `BLOCKED`
host certification, records `migration_authorized: false`, and exits with
status 2. The command does not retain its temporary synthetic fixtures.

The reference adapter proves that the acceptance contract is executable and
that the repository's current package, backup, restore, and public-build
primitives can meet it in isolated local fixtures. It does **not** prove a
future provider's authentication, row policy, object ACL, encryption, deletion
guarantee, egress control, or hosted log pipeline. When a provider is selected,
its adapter must run this same contract in a disposable environment and attach
the resulting report plus provider-specific ACL, cache, retention, restore, and
log evidence. Until that occurs, those hosted claims remain unproven and no
private draft may be migrated.

## 8. Implementation gate and prohibited work

Owner approval must be recorded against this document after review of:

- the selected hosting and identity providers, including data location and
  contractual deletion guarantees;
- the threat model, workspace/role matrix, client-record policy, key ownership,
  retention schedule, incident response, and restore runbook;
- an implementation plan that preserves loopback mode and does not migrate
  existing drafts automatically;
- the complete leak-prevention evidence in Section 7;
- a manual review of a real or synthetic client-overlay package, with no
  private content added to this public repository.

Until the design approval, separate implementation authorization, and required
acceptance evidence all exist, do not:

- bind the workbench to a non-loopback interface or add a Replit workflow;
- add an authentication connector, provider SDK, model call, or hosted
  database/object store;
- upload `.foundry-data/`, local backups, client records, or generated ZIPs;
- add hosted URLs, public API routes, remote telemetry, or deployment secrets;
- describe the workbench as multi-user, hosted, encrypted, or production-ready.

The next implementation, if approved, must be a separate task with an explicit
provider choice, migration opt-in, test fixtures, and a rollback plan. This
document does not authorize that task.

## 9. Owner decision record

The owner reviewed and approved this boundary as written on 2026-09-14. The
approval records these deployment-policy decisions:

- **Identity and hosting posture:** approve the provider-independent identity,
  authentication, authorization, and hosting requirements in this document.
  Provider selection, data location, contractual deletion guarantees, and the
  disaster-recovery region remain deferred until a separate implementation
  proposal.
- **Client-record policy:** approve the strict isolated/private policy in
  Section 5. Client records remain a separate privacy class and cannot enter the
  public portfolio workspace, public artifact, model training, product
  analytics, or cross-client processing.
- **Retention:** approve daily database snapshots and destructive-action
  recovery points for 35 days, weekly long-term recovery points for 12 weeks,
  generated ZIP retention for 7 days by default, and content-free audit records
  for 12 months. Explicit holds continue until released.
- **Key ownership:** encryption keys must be owner-controlled and separate from
  the data service. Provider-managed-only key ownership is not approved.
- **Recovery objectives:** the recovery point objective is 24 hours and the
  recovery time objective is 72 hours. The disaster-recovery region remains a
  provider-selection decision.
- **Migration:** existing local drafts may migrate only through explicit
  per-project owner opt-in. Migration is never automatic, and continuing in
  loopback mode cannot require migration.

This approval closes the design-review gate only. It does not satisfy the
implementation evidence in Section 7 and does not authorize a Replit workflow,
non-loopback binding, authentication connector, hosted data service, object
vault, provider or model call, telemetry, deployment secret, or upload of
private state. The loopback-only and no-provider-call constraints remain in
force until a separate implementation task is expressly authorized.

## 10. Hosted certification decision

On 2026-09-15, the owner declined to select or use a hosted provider. Therefore:

- no provider adapter, hosted identity, database, object vault, cache, backup
  service, logging pipeline, workflow, or deployment was created;
- hosted certification was not run and must be reported as `BLOCKED`, not
  `PASS`;
- the provider-independent reference harness remains a local contract test
  only;
- no real drafts, client data, local backups, generated packages, or
  `.foundry-data/` content were used or moved;
- existing local drafts remain loopback-only and unmigrated;
- migration remains unauthorized unless the owner later selects a provider and
  separately approves a new hosted certification and per-project migration.
