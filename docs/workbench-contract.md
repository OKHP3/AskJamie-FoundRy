# Workbench implementation contract v1

Private, single-user local application. Python 3.11, existing PyYAML/jsonschema, SQLite, standard-library HTTP server bound to 127.0.0.1 only. Plain HTML/CSS/JS, no frontend build or external runtime dependencies. No provider calls or arbitrary code execution. Program starts with `python3 -m workbench --port 8765`; data in ignored `.foundry-data/` (override `--data-dir`). Coordinator owns governance/research/docs and final integration. Backend owns `workbench/*.py` and unit tests. Frontend owns `workbench/static/` only.

## HTTP

JSON requests/responses. Errors `{error: string}` with 400 invalid, 404 missing, 409 stale revision. Limit bodies to 1 MiB. Reject invalid JSON, malformed types and unknown fields. All responses no-store. Strict local Host and same Origin on state-changing requests, require JSON content type plus `X-Foundry-Request: 1` to prevent cross-origin writes. Static routes explicitly allowlisted, no filesystem browsing. No arbitrary URL fetching.

- GET `/api/health` -> `{status:"ok"}`
- GET `/api/projects` -> `{projects: Project[]}`
- POST `/api/projects` accepts Draft, returns Project (201)
- GET `/api/projects/{id}` -> Project
- PUT `/api/projects/{id}` accepts Draft plus `revision` for optimistic concurrency, returns Project; immutable ID, increment revision; snapshots saved in SQLite
- GET `/api/projects/{id}/history` -> `{history:[{revision,updated_at}]}`
- GET `/api/projects/{id}/validate` -> `{valid:boolean,errors:string[],warnings:string[],repo:string}`
- POST `/api/projects/{id}/preview` with `{answers:{nodeId:boolean}}` -> `{complete:boolean,result:string|null,next:{id,question}|null,trace:string[]}`. Only decision-tool kind.
- POST `/api/projects/{id}/evaluate` with `{}` -> `{revision,passed,failed,unrun,cases:[{name,status,detail}],evaluated_at}`; persists record tied to revision. Do not mark missing supplied response as pass.
- GET `/api/projects/{id}/evaluations` -> `{evaluations: Evaluation[]}`
- GET `/api/projects/{id}/export` -> ZIP, blocked with 400 if invalid; private package, no publication; response Content-Disposition safe slug filename
- GET `/api/registry` -> `{repositories: array, note: string}` from current canonical YAML, read-only
- GET `/api/skills` -> `{sourceRepository,sourceCommit,generatedAt,retrievedAt,skills:[{id,name,family,description,maturity,evidenceStatus,sourceUrl}]}` from committed public Skillz metadata snapshot `workbench/data/skills.json`; coordinator provides snapshot, backend just reads it. No skill execution/import.

## Data

Draft has exact fields (defaults allowed):
`title`, `slug`, `code` (aj01-aj99 or brg00-brg99; export reserves existing non-overlay codes), `family` (core-capability, brandguard, enterprise-sleuth, client-overlay, conversation-design, rag-experiment), `kind` (assistant, decision-tool, workflow), `purpose`, `audience`, `source_text`, `source_reference`, `instructions`, `output_contract`, `constraints`, `client_org`, `parent_capability`, `bfs_firewall` (bool), `visibility_lock` (empty or permanent-private), `skill_ids` (string array), `workflow_steps` (string array), `decision` (graph), `eval_cases` (array). Visibility always private, public_graduation_allowed false for all draft exports. No public control accepted. Any client_org, client-overlay, bfs_firewall or visibility_lock enforces permanent-private; once protected, updates cannot clear or change original client identity, family from client-overlay, or protection flags.

Project adds `id` (uuid), `revision` (int), `created_at`, `updated_at`, `visibility:"private"`, `public_graduation_allowed:false`. Cannot accept those derived values as client inputs except PUT revision.

Code is checked against registry conflicts on export. Client-overlay uses its parent code and must reference a governed non-client parent with matching code; other families cannot reuse reserved registry codes. Code aj00 invalid. UI default aj05. Repo name `askjamie-{code}-{slug}` or `{client_org}-askjamie-{code}-{slug}`. Slug/org ASCII lower letters/digits and single interior hyphens. Draft saving allows incomplete content; type/size/security invariants always enforced. Export readiness additionally requires title, purpose, audience, source_text/source_reference, instructions, output_contract; no template placeholders in generated template text. Do not scan raw user source for placeholder-like prose.

Decision graph: `{start:"start",nodes:[{id:"start",question:"Is the request clear?",yes:"answer",no:"clarify"},{id:"answer",result:"Proceed with the agreed scope."},{id:"clarify",result:"Ask for missing context."}]}`. Unique IDs, reachable nodes, no cycles or dangling edges; question nodes require yes/no targets; terminal nodes require nonempty result. Preview follows answers until first unanswered node. Missing answer is not false. Graph errors must be reported before run/export.

Eval cases for decision-tool: `{name,answers:{id:boolean},expected_result:string}`. Other kinds: `{name,input,response,required:string[],forbidden:string[]}`. Blank response -> unrun. Explicitly label supplied-response text checks; they do not run an AI. Empty suite gives unrun/no evidence. UI provides usable editing for both forms.

## Export

Copy canonical `_template/` directory layout and license, render its placeholder documents using concrete project data; retain provenance of template base. Generate schema-valid manifest, `origin/source.md`, `skill/instructions.md`, `prompts/system.md`, `docs/specification.md`, `tests/evals.json`, `exports/project.json`, `exports/registry-proposal.yaml`, `research/skills.json` and `exports/evaluation-records.json` (revision-aware). Registry proposal is explicitly pending, not applied. Workflow includes ordered checklist. Decision package includes `decision.json` plus standalone `index.html` that runs graph offline, escapes content, allows restart and displays result. Include readable README usage. Nothing outside current project or selected public skill metadata enters ZIP. Never include entire registry, data DB or other projects.

## UI

AskJamie profile v1.1.0: dark brown #1e1a17/#2a2420/#231f1c, foreground #e8e4df, teal #4ba8bd, muted #9e918a only secondary. Heading Baloo 2, body Open Sans with approved fallbacks, no external font requests unless vendored with license. Calm helpdesk, sidebar workbench/projects/skills/universe/registry, primary create-project route, intentional empty state and demo-template choice (do not seed fake records). Editor sections Brief, Behavior, Decision/Workflow, Evidence, Package. Visible save/dirty state and failure messages, no silent data loss on navigation. Editor JSON advanced fields acceptable only alongside usable guided decision/evaluation controls. Selected skills via picker. Safe DOM text insertion. Responsive at 390 and 1440px, keyboard focus, accessible labels/live errors. Three overlapping rings AskJamie left, OverKill center, Glee-fully right, Skillz visibly shared. All seven elements labeled. OverKill Found-Ry explicitly regional.

## Review clarifications

- Protection starts on the first saved protected revision, including creation.
  Compare incoming updates against the stored prior state inside the transaction.
- Client identity requires client-overlay family and a valid governed non-client
  parent with matching code. Client overlays can reuse that parent code.
- Existing and archived codes remain reserved for non-overlay projects. Check
  full generated repo name too. Omit unset optional manifest fields.
- Registry proposal retains parent_capability. Registry schema includes the two
  extra capability families already supported by manifest.schema.yaml.
- Resolve every unique selected skill ID against the supplied immutable metadata
  snapshot and preserve its source commit in exports.
- Exclude `_template/ABOUT.md` from child output. Render every placeholder-bearing
  template document and check generated documents after rendering.
- Preserve source_reference verbatim; it is an owner-supplied provenance claim,
  not independent source verification. Include export time, project revision and
  SHA-256 of source_text so the original input is traceable.
- Escape `<`, `>`, `&`, U+2028 and U+2029 when embedding JSON in offline HTML.
- Decision answers must name graph question nodes; require boolean values.
  Text evaluation matching is literal, case-sensitive substring matching.
- Reject missing/invalid/oversized Content-Length or Transfer-Encoding on writes;
  never read beyond the declared bounded body. Local registry display may show
  private metadata to the local owner, but exports never include unrelated rows.
