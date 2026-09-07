# Seven elements, three regions, one shared skill catalog

Research date: September 7, 2026. Audience: Jamie Hill and AskJamie Found-Ry implementers.

## Decision

Develop AskJamie Found-Ry as a private capability-building workbench for interpretive assistants, decision tools and guided workflows. Use Skillz as a shared, provenance-bearing catalog. Keep OverKill Found-Ry and Glee-fully Found-Ry distinct regional workbenches. Preserve existing lineage metadata as historical provenance, not permission to import another region's private content.

This relationship is owner-directed in the September 7 request. The public sites support distinct roles, but some older documents use a parent-relay hierarchy or describe non-overlapping roles. The owner's overlapping-rings model controls this implementation. The overlap represents collaboration and reusable skills, not merged ownership.

## The seven elements

| Element | Region and purpose | Verified functionality | Boundary for this build |
|---|---|---|---|
| [OverKill Hill](https://overkillhill.com/) | Connective center, methodology, strategy and systems practice | Static public site with project pages, writing, search and site validation utilities | Universe context and governance; portfolio presence does not establish every linked product's readiness |
| [Skillz](https://okhp3.github.io/skillz/) | Shared catalog accessible across all regions | Searchable skill contracts, families, comparisons, curated stacks and browser-local composition | Read-only reference and reuse; preserve maturity, evidence and source metadata |
| [OverKill Found-Ry](https://okhp3.github.io/OverKill-Hill-FoundRy/) | OverKill's own system-creation workshop | Public browser-based Custom GPT Creator with local project state, build stations, audit/compare/export surfaces | Public GitHub exposure does not make it a shared regional dependency |
| [Glee-fully Tools](https://glee-fully.tools/) | Everyday personal tools and approachable execution | Static catalog, seven branch hubs, 42 Tool-ette pages, search and Arcade routing | Catalog publication states are distinct from externally hosted GPT behavior |
| [Glee-fully Tools Found-Ry](https://github.com/OKHP3/Glee-fullyTools-FoundRy) | Glee-fully fabrication and governance | Ledgers, tone frameworks, PromptChain, FrankenTemplate, evaluation and inventory artifacts | Separate regional source family; current source says it is not a deployable application |
| [AskJamie](https://askjamie.bot/) | Interpretive intelligence: clarity, tradeoffs and next steps | Static portfolio of lenses, prototypes and public-information BrandGuard examples | Early-access public evidence, not proof of one integrated assistant runtime |
| [AskJamie Found-Ry](https://github.com/OKHP3/AskJamie-FoundRy) | AskJamie capability fabrication and governance | At research baseline: templates, manifests, nine registry entries, skills and Python validators | Target of the new application; private by default; locked client material remains isolated |

## What the evidence changes

**Skillz is usable infrastructure, but its entries have different evidence levels.** The published catalog identifies 342 skills in 20 families at source commit `1a8686c`. Its summary records 263 draftable, 74 skeleton and five usable skills. These are catalog metadata, not independently established production performance. The workbench should retain those fields when a skill is selected, with source links and the snapshot date. A selected contract does not execute itself. Sources: [published catalog](https://okhp3.github.io/skillz/data/catalog.json), [published summary](https://okhp3.github.io/skillz/data/project-summary.json), [catalog generator](https://github.com/OKHP3/skillz/blob/7616ccd7c92b65dafc936f744208ba62507b3c5c/artifacts/forge/scripts/build-catalog.js).

**The three public brands do different jobs.** AskJamie describes a calm helpdesk that translates between strategy and execution, with diagrams and walkthroughs. Glee-fully describes a personal toolbox and explicitly reports one live, 24 beta and 17 unavailable Tool-ettes. OverKill describes protocol-driven systems practice and makes projects inspectable. Together these support a workbench centered on explicit behavior, decisions and evidence, rather than copying another brand's visual or capability system. Sources: [AskJamie](https://askjamie.bot/), [Glee-fully](https://glee-fully.tools/), [OverKill](https://overkillhill.com/).

**Public exposure and private governance are different facts.** Authenticated GitHub metadata confirms that OverKill Found-Ry is a public repository and its browser creator is accessible. Its manifest nevertheless describes a private relay with permanent visibility controls. This is a confirmed repository-policy mismatch, not evidence that all governed materials are approved for sharing. The new AskJamie application will reference the public surface in its universe map without copying its private creator assets or capabilities. Sources: [public creator](https://okhp3.github.io/OverKill-Hill-FoundRy/), [manifest at verified HEAD](https://github.com/OKHP3/OverKill-Hill-FoundRy/blob/312256af6d5528df882e2b3263c29cffcd586162/manifest.yaml), [creator source](https://github.com/OKHP3/OverKill-Hill-FoundRy/tree/312256af6d5528df882e2b3263c29cffcd586162/artifacts/custom-gpt-creator).

**AskJamie already has useful building contracts.** Its template defines required directories and lineage; its brand skill defines a calm dark-brown and teal helpdesk; its repository-creation skill distinguishes interpretation from Glee-fully execution and OverKill strategy. Preserve these assets and put a runtime around them. Nine registry records describe governed identities; no remote child existence or deployment is implied. Sources: [baseline template](https://github.com/OKHP3/AskJamie-FoundRy/tree/a687f68c091c4507cf76fc48b78224ed592b38cb/_template), [registry](https://github.com/OKHP3/AskJamie-FoundRy/blob/a687f68c091c4507cf76fc48b78224ed592b38cb/registry/index.yaml), [brand profile](https://github.com/OKHP3/AskJamie-FoundRy/blob/a687f68c091c4507cf76fc48b78224ed592b38cb/.agents/skills/okhp3-askjamie-brand/references/askjamie.yaml).

## Current-source ledger

All GitHub heads were retrieved on September 7, 2026. Website retrieval confirms accessible content, not exhaustive interaction testing or deployment parity.

| Source, publisher OKHP3 | Verified main commit | Claim supported |
|---|---|---|
| [OverKill Hill source](https://github.com/OKHP3/OverKill-Hill/tree/9c186345333a2cbb965805c65f43d294aadfc0ae) | `9c186345333a2cbb965805c65f43d294aadfc0ae` | Static site and connective methodology |
| [Skillz source](https://github.com/OKHP3/skillz/tree/7616ccd7c92b65dafc936f744208ba62507b3c5c) | `7616ccd7c92b65dafc936f744208ba62507b3c5c` | Generated catalog and read-only contract browsing |
| [OverKill Found-Ry source](https://github.com/OKHP3/OverKill-Hill-FoundRy/tree/312256af6d5528df882e2b3263c29cffcd586162) | `312256af6d5528df882e2b3263c29cffcd586162` | Creator source plus private relay controls |
| [Glee-fully source](https://github.com/OKHP3/Glee-fullyTools/tree/4cc42218a32d154c513ffbf80d102f767015a4f4) | `4cc42218a32d154c513ffbf80d102f767015a4f4` | Consumer catalog, lifecycle and routing |
| [Glee-fully Found-Ry source](https://github.com/OKHP3/Glee-fullyTools-FoundRy/tree/a190c026cf9e910fc843eb14562f22c51278947f) | `a190c026cf9e910fc843eb14562f22c51278947f` | Regional workbench, not current application runtime |
| [AskJamie source](https://github.com/OKHP3/AskJamie/tree/7de1472025b38d7d763a9e5696b7118b482b2fad) | `7de1472025b38d7d763a9e5696b7118b482b2fad` | Lens portfolio and public-information case studies |
| [AskJamie Found-Ry baseline](https://github.com/OKHP3/AskJamie-FoundRy/tree/a687f68c091c4507cf76fc48b78224ed592b38cb) | `a687f68c091c4507cf76fc48b78224ed592b38cb` | Private governance workbench, templates and nine records |

## Gaps and contradictions

| Claim or gap | Confidence and disposition | Follow-up |
|---|---|---|
| Regional roles and sharing | High: owner instruction, corroborated in public positioning | Implement explicit regional ownership and shared Skillz links |
| Older ecosystem map calls OverKill Found-Ry a parent for all domains | Confirmed contradiction with current direction | Replace explanatory map; retain manifest lineage provenance |
| Skillz published snapshot is behind current GitHub head | Confirmed source metadata difference | Display snapshot source, never claim latest-main synchronization |
| Catalog or registry entries prove functioning downstream tools | Unsupported | Show recorded status and readiness separately |
| Replit workspace and parity | Browser observations now cover all seven attempts; all seven eventually loaded workspace identities. Early Page not found observations were superseded. Commit parity remains unverified | Preserve remote work; inspect hashes before synchronization |
| Public creator equals entire private OverKill relay | Unsupported | Keep public surface and private materials distinct |
| Multiuser or internet-hosted AskJamie Found-Ry | Not part of verified baseline | Local single-user runtime first; hosted auth is a separate deployment design |

All seven supplied Replit locators and later authenticated Browser observations are recorded in [replit-access.md](replit-access.md). Research stopped after two bounded source lanes, coordinator checks, targeted contradiction resolution and shared read-only Browser observations. The roles and build boundaries have sufficient support; exact Replit commit parity remains a bounded gap. These findings support an independent local implementation without overwriting remote work.

## Application acceptance criteria

1. Start locally using the existing Python 3.11 baseline and pinned dependencies.
2. Save, reopen and revise capability drafts in SQLite, including source provenance and selected Skillz references.
3. Author assistant behavior, guided workflow steps and executable yes/no decision graphs. Run decision paths without a paid model service.
4. Run deterministic decision tests; retain supplied-response checks as recorded evidence, never imply model execution.
5. Generate a downloadable repository ZIP from `_template/`, including valid manifest, original source, instructions, decision runtime where applicable, evaluations and a proposed registry entry.
6. Enforce naming and permanent-private rules on the server; never update the canonical registry simply because a draft was saved or exported.
7. Provide responsive, keyboard-usable AskJamie styling and a three-ring map with Skillz marked shared.
8. Test persistence, stale revisions, hostile inputs, graph validation, export contents and protected-data boundaries. Document any unavailable visual verification.

A generated assistant package is an authored instruction/specification asset. Only decision-tool exports include a deterministic executable runtime. No automatic external GPT provisioning, code execution agent, remote repository creation or public graduation is claimed.
