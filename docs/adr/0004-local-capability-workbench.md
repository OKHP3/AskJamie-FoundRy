# ADR-0004: Local capability-building workbench

## Status

Accepted for implementation by owner direction, 2026-09-07.
Supersedes ADR-0001's exclusion of application runtime. Its governance relay
and authoritative scaffold responsibilities remain in force.

## Context

The owner requested a functioning AskJamie Found-Ry application for building
systems and tooling after researching the seven universe elements. Existing
source supplies templates, schemas, skills and registry metadata, but no app.

## Decision

Add a single-user Python/SQLite application with a plain browser interface.
It authors private capability drafts, runs deterministic decision paths,
records evaluation evidence and exports template-based packages. Skillz is
consumed as immutable public metadata. Sibling Found-Ry materials are not
runtime dependencies. Preserve historical lineage and owner privacy controls.

## Alternatives

A static browser-only tool would avoid a server but rely on browser storage for
private source and revisions. A hosted service would need authentication,
operations and a deployment decision. The local database gives explicit,
portable storage using existing Python dependencies at low operating cost.

## Consequences

The repository now owns application runtime and tests. Local drafts remain
separate from the authoritative child registry. A generated package is not a
remote child repository, production assistant or graduation approval. Hosted
multiuser use, model-provider execution and arbitrary code execution require
separate decisions. Existing Python governance commands remain supported.

## Evidence

- [Universe research](../research/2026-09-07-universe/universe-research.md)
- [Application contract](../workbench-contract.md)
- [Operating guide](../workbench.md)
