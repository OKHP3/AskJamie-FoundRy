# Hosted authoring boundary design

**Status:** design only, owner review required
**Applies to:** a possible future multi-device or multi-user AskJamie authoring
runtime
**Current decision:** keep authoring loopback-only. Do not host this workbench,
add a provider integration, or move existing drafts online until this design is
approved and its acceptance evidence exists.

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

The following is the bounded proposal to approve or revise before selecting a
host. It is not a claim about the current local backup behavior.

| Item | Required handling | Proposed retention |
|---|---|---|
| Database backup | Encrypted, workspace-aware backup; encryption keys are separate from the data service; access is owner-only | Daily snapshots for 35 days |
| Recovery points | Immutable copy before destructive migration, restore, or deletion; tagged with actor and reason | 35 days unless a hold applies |
| Long-term recovery | Encrypted weekly restore point with a tested manifest and checksum | 12 weeks |
| Release or governance hold | Explicit owner-created hold with expiry or review date | Until the hold is released |
| Generated ZIP | Encrypted private object, no public cache, no anonymous link | 7 days by default, then delete |
| Audit record | Keep action, actor, workspace, object class, result, and timestamp; do not store source content | 12 months, subject to owner policy |

Backups must not be treated as a second public export path. Restore is performed
into an isolated, access-controlled environment first. A restore is not complete
until schema validation, checksum verification, workspace-isolation tests, and
public-route checks pass. Retention jobs must report failures and must not
silently claim deletion when a provider copy remains.

The owner must approve the final retention periods, deletion guarantees, key
ownership, disaster-recovery region, recovery point objective, and recovery time
objective. Those decisions are deployment-specific and cannot be inferred from
the local SQLite implementation.

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

## 8. Approval gate and prohibited work before approval

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

Until that approval exists, do not:

- bind the workbench to a non-loopback interface or add a Replit workflow;
- add an authentication connector, provider SDK, model call, or hosted
  database/object store;
- upload `.foundry-data/`, local backups, client records, or generated ZIPs;
- add hosted URLs, public API routes, remote telemetry, or deployment secrets;
- describe the workbench as multi-user, hosted, encrypted, or production-ready.

The next implementation, if approved, must be a separate task with an explicit
provider choice, migration opt-in, test fixtures, and a rollback plan. This
document does not authorize that task.
