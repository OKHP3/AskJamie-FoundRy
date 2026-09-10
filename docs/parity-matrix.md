# AskJamie FoundRy parity matrix

Status: owner review required. This matrix records a regional adaptation of the
OverKill-Hill-FoundRy mentor pattern. It does not authorize public graduation,
hosted authoring, child-repository creation, or deployment of a capability.

## Evidence baseline

| Evidence | What it establishes |
|---|---|
| OverKill-Hill-FoundRy commit `8de1eb2` inspected 2026-09-09 | A public pnpm/React workbench, Custom GPT studio, backup/import and lifecycle controls, governance and graduation audits, browser coverage, and Pages delivery exist in the mentor repository |
| `https://okhp3.github.io/OverKill-Hill-FoundRy/` returned HTTP 200 on 2026-09-09 | The mentor’s Pages artifact is deployed and reachable; it does not prove hosted authoring or private-state exposure is appropriate here |
| AskJamie main baseline through 2026-09-09 | Python standard-library/SQLite loopback workbench, private exports, immutable Skillz metadata, decision/evaluation flows, governance validators, and browser acceptance already exist |
| `manifest.yaml` and `AGENTS.md` | AskJamie owns interpretation and private fabrication; OverKill is the mentor/centroid; public source visibility does not prove operation |

## Decisions

`adopt` means the capability is safe and useful in AskJamie’s private runtime.
`adapt` means the intent is retained with different regional naming or a
read-only boundary. `defer` means evidence or access design is still required.
`out of scope` means copying it would violate the current runtime or privacy
boundary.

| Reference capability | Decision | AskJamie owner and adaptation | Privacy impact | Acceptance proof |
|---|---|---|---|---|
| Public source orientation and relationship map | adapt | Coordinator: `public/` is an AskJamie-branded static Pages artifact covering AskJamie, OverKill, Glee-fully, and shared Skillz | Public content only; no API, local storage, SQLite, drafts, client records, secrets, or packages | `scripts/build-public-artifact.py --build`; `tests/test_public_artifact.py`; relative asset and local HTTP 200 checks |
| Capability workbench brief, behavior, target, and phase | adopt | Workbench owner: guided fields retain the AskJamie assistant, decision-tool, and workflow model, with target and lifecycle phase labels | Fields are local draft content and remain behind loopback | Python suite plus browser creation/edit/save journey |
| Evidence and review gates | adapt | Workbench owner: source provenance, evidence notes, Skillz metadata, evaluation cases, validation, and package review remain explicit; supplied-response checks remain non-AI checks | Source and client material stay in private SQLite and private exports | Export/evaluation acceptance and UI package tab |
| Custom GPT / assistant flow | adapt | Capability owner: assistant behavior is authored as a portable specification and can name `openai-custom-gpt` as a planning target; no provider call or provisioning | No credentials or provider payloads are accepted | Model contract, export metadata, and docs explicitly state manual platform handoff |
| Project lifecycle controls | adopt | Workbench owner: confirmed duplicate creates a new revision-one private draft; confirmed delete cascades history/evaluations | Destructive actions are local and explicit; no remote deletion | Store and HTTP tests plus browser duplicate/delete journey |
| Versioned backup/export and import/restore | adopt | Workbench owner: version-one JSON envelope, complete preflight validation, explicit replace confirmation, atomic replacement | Backup files may contain all private drafts; download/import stays loopback-only | Recovery tests prove revisions/evaluations survive and malformed import preserves current state |
| Malformed-data recovery | adopt | Workbench owner: invalid shape, IDs, revisions, drafts, and references fail before mutation with visible errors | Existing private state is not cleared by a malformed replacement | Invalid-import regression and API error assertions |
| Optimistic concurrency and protection | adopt | Existing backend owner: stale revisions, client identity, BFS firewall, lineage, and permanent-private locks remain unchanged | Prevents silent overwrites and privacy downgrades | Existing workbench/boundary suite remains green |
| Immutable shared Skillz catalog | adopt | Coordinator/backend: retain committed snapshot and provenance; selections are references, not execution/import | Public metadata may be shown; selected project content remains private | Snapshot loader, skills UI, and export tests |
| Registry and graduation audits | adapt | Governance owner: registry remains read-only in the workbench; exports are pending proposals; `public_graduation_allowed: false` remains locked | No UI mutation or automatic child publication | Registry validation and generated private package assertions |
| Broader mentor governance/graduation surfaces | defer | Governance owner: document the gap and require an owner-approved audit design before adding | Could expose or promote protected material if copied prematurely | This matrix and maturation docs record the unresolved difference |
| Multi-artifact pnpm/React authoring runtime | out of scope | Runtime owner: retain Python standard library/SQLite and plain static UI | Replacing it would change state handling and could invite unintended hosting | Workbench contract and Replit guidance retain Python loopback operation |
| Hosted multi-user authoring, auth, model calls, paid inference | defer | Owner decision required after the [hosted authoring boundary design](hosted-authoring-boundary.md), including authentication, workspace routing, client-record handling, retention, and leak-prevention proof | High risk: would move private source and drafts across a trust boundary; the first hosted authoring release must make no model, inference, external-data, or arbitrary-URL provider call | Design is explicitly non-authorizing; owner approval and the Section 7 evidence set are required before any hosted runtime |
| Automatic child repositories, public graduation, package deployment | out of scope | Governance owner: keep proposals pending and capabilities private | Prevents accidental publication of client or draft material | Export proposal, manifest controls, and CI do not publish packages |
| Mentor Pages deployment workflow | adapt | Release owner: provide a manual Pages workflow and optional deployed URL smoke check, without auto-publishing from normal CI | Only `public/` is eligible for upload | Manual workflow builds `dist/pages`, deploys only when dispatched, and curls its output URL |

## Acceptance boundary

The accepted surface is a public, read-only orientation artifact plus a private
loopback authoring workbench. The matrix is complete for this parity pass when
the mechanical checks and judgment checks in the final validation record pass.
Any hosted authoring, model quality, public graduation, or child-repository
claim remains unresolved until the separately approved design and evidence in
[`hosted-authoring-boundary.md`](hosted-authoring-boundary.md) exist.
