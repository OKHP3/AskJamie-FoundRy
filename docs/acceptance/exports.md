# Export Acceptance

Scope:

- F05: Execute an exported decision runner in a permitted local browser context, including Yes/No/restart.
- F06: Check generated ZIP path safety and isolation.
- F07: Validate generated manifests and registry proposals for assistant, workflow and decision exports.
- F08: Verify exported hostile text is inert and keep the regression evidence reproducible.

Automated checks:

- `python3 -m unittest tests.test_export_acceptance`

Browser runner:

- `python3 tests/browser/export-runner.py /path/to/generated-export.zip`
- Open the printed `http://127.0.0.1:<port>/index.html` URL in the permitted local browser.
- Confirm the decision page shows `Yes`, `No`, `Restart`, and that hostile source text does not surface as active markup.

Evidence notes:

- ZIP entries must stay within the archive root and never leak sibling project content.
- Generated `manifest.yaml` files must validate against `schemas/manifest.schema.yaml`.
- Generated registry proposals must validate against the item schema in `schemas/registry.schema.yaml`.
- Decision exports must keep the runner offline, text-based, and restartable.

Observed smoke result:

- 2026-09-08: exported decision runner opened in a local browser context, rendered `Yes`, `No`, and `Restart`, and preserved hostile result text as plain text with no injected elements.
