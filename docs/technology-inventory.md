# Technology inventory and update policy

Updated: 2026-09-07

The repository combines governance utilities with a local single-user
capability-building application. It has no frontend compilation step.

| Technology | Role and policy |
|---|---|
| Python 3.11 | Supported baseline for workbench and governance utilities |
| PyYAML 6.0.3 | Existing pinned YAML dependency |
| jsonschema 4.26.0 | Existing pinned JSON Schema validation dependency |
| SQLite | Python standard-library durable draft, revision and evaluation store |
| HTTP server | Python standard-library, loopback only, local use |
| HTML/CSS/JavaScript | Static same-origin interface; no npm runtime dependencies |
| GitHub Actions | Compatibility workflow runs validators and unittest suite |
| Replit | Existing Python/Nix project metadata retained; live workspace not verified |

The standard-library HTTP server is for the local workbench. It is not an
internet production hosting design. See [Python's HTTP documentation](https://docs.python.org/3.11/library/http.server.html).
SQLite supports durable local storage without a separate database service:
[Python SQLite documentation](https://docs.python.org/3.11/library/sqlite3.html).

Dependabot tracks pinned Python dependencies and Actions. Runtime migrations
and authenticated hosted deployment remain explicit follow-up changes.
