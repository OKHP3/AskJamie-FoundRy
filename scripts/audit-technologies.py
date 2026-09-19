#!/usr/bin/env python3
"""Read-only release audit. Writes reports, never installs or edits dependencies."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.metadata as metadata
import gzip
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import ssl
import subprocess
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zlib

ROOT = Path(__file__).resolve().parents[1]
TRANSITIVE = ("attrs", "jsonschema-specifications", "referencing", "rpds-py",
              "typing-extensions", "pyee", "greenlet", "pip")


def version_key(value: str) -> tuple[int, ...]:
    """Accept numeric final releases only; never guess prerelease ordering."""
    if not re.fullmatch(r"v?\d+(?:\.\d+){0,3}", value):
        raise ValueError(f"Not a supported stable version: {value}")
    parts = tuple(int(p) for p in value.removeprefix("v").split("."))
    return parts + (0,) * (4 - len(parts))


def newest(versions: list[str]) -> str:
    if not versions:
        raise ValueError("No stable release found in upstream response")
    return max(versions, key=version_key).removeprefix("v")


def fetch(url: str) -> str:
    headers = {"User-Agent": "AskJamie-FoundRy-technology-audit", "Accept": "application/json,text/html"}
    # Only attach the ephemeral token to the GitHub API, never package sites.
    if urlparse(url).hostname == "api.github.com" and os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request(url, headers=headers), timeout=30) as response:
        body = response.read(8_000_001)
    if len(body) > 8_000_000:
        raise ValueError("Upstream response exceeded the audit size limit")
    # Some official sites send gzip even without Accept-Encoding negotiation.
    if body.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed:
            body = compressed.read(8_000_001)
        if len(body) > 8_000_000:
            raise ValueError("Expanded upstream response exceeded the audit size limit")
    return body.decode("utf-8")


def stable_release(watch: dict, body: str) -> str:
    kind = watch["kind"]
    if kind == "regex":
        return newest(re.findall(watch["pattern"], body))
    data = json.loads(body)
    if kind == "pypi":
        advertised = data.get("info", {}).get("version", "")
        if advertised and not re.fullmatch(r"\d+(?:\.\d+){1,3}", advertised):
            # A post/epoch/local release is not a prerelease. Reject unsupported
            # final syntax instead of silently claiming an older numeric pin is latest.
            if not re.search(r"(?:a|b|rc|dev)\d+", advertised):
                raise ValueError("Unsupported PyPI final release syntax")
        now = datetime.now(timezone.utc).isoformat()
        versions = []
        for version, files in data["releases"].items():
            if not re.fullmatch(r"\d+(?:\.\d+){1,3}", version):
                continue
            if any(not f.get("yanked", False) and
                   f.get("upload_time_iso_8601", "9999") <= now for f in files):
                versions.append(version)
        return newest(versions)
    if kind == "github":
        if data.get("draft") or data.get("prerelease"):
            raise ValueError("GitHub returned a draft or prerelease")
        version = data["tag_name"]
    elif kind == "npm":
        version = data["version"]
    elif kind in {"node-lts", "node-current"}:
        today = datetime.now(timezone.utc).date().isoformat()
        return newest([r["version"] for r in data if r["date"] <= today and
                       (kind == "node-current" or r.get("lts"))])
    else:
        raise ValueError(f"Unsupported source kind: {kind}")
    version_key(version)
    return version.removeprefix("v")


def discover(root: Path) -> list[dict]:
    watches = []
    for relative in ("requirements.txt", "tests/browser/requirements.txt"):
        for number, line in enumerate((root / relative).read_text().splitlines(), 1):
            line = line.partition("#")[0].strip()
            if not line:
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==(\d+(?:\.\d+){1,3})", line)
            if not match:
                raise ValueError(f"Unsupported requirement at {relative}:{number}: {line}")
            name, version = match.groups()
            watches.append({"name": name, "kind": "pypi", "current": version,
                            "url": f"https://pypi.org/pypi/{name}/json",
                            "evidence": f"{relative}:{number}", "owner": "Dependabot update PR"})
    actions: dict[str, dict] = {}
    for path in sorted((root / ".github/workflows").glob("*")):
        if path.suffix not in {".yml", ".yaml"}:
            continue
        for name, ref in re.findall(r"uses:\s*([\w.-]+/[\w.-]+)@([^\s#]+)", path.read_text()):
            actions[name + "@" + ref] = {
                "name": name, "kind": "github", "current": ref,
                "url": f"https://api.github.com/repos/{name}/releases/latest",
                "evidence": str(path.relative_to(root)).replace("\\", "/"),
                "owner": "Dependabot update PR", "floating_major": bool(re.fullmatch(r"v\d+", ref))}
    return watches + list(actions.values())


def check(watch: dict, loader=fetch) -> dict:
    row = dict(watch)
    try:
        row["latest"] = stable_release(watch, loader(watch["url"]))
        current = watch.get("current", watch.get("reviewed"))
        latest_key = version_key(row["latest"])
        current_key = version_key(current)
        if watch.get("floating_major"):
            if latest_key[0] == current_key[0]:
                status = "TRACKING"
            elif latest_key[0] > current_key[0]:
                status = "UPDATE"
            else:
                status = "UNKNOWN"
                row["error"] = "Action major is newer than upstream stable response"
        elif latest_key > current_key:
            status = "UPDATE" if "current" in watch else "REVIEW"
        elif latest_key == current_key:
            status = "CURRENT" if "current" in watch else "REVIEWED"
        else:
            status = "UNKNOWN"
            row["error"] = "Observed baseline is newer than the upstream stable response"
        row["status"] = "AVAILABLE" if watch.get("advisory") and status == "UPDATE" else status
    except Exception as error:
        row["status"] = "UNKNOWN"
        # No response bodies, headers, credentials or full network errors in logs.
        code = getattr(error, "code", None)
        row["error"] = f"{type(error).__name__}" + (f" HTTP {code}" if code else "") + ": release lookup or version parsing failed"
    return row


def environment() -> dict:
    installed = {}
    for name in ("PyYAML", "jsonschema", "playwright") + TRANSITIVE:
        try:
            installed[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            installed[name] = None
    result = {"python": sys.version.split()[0], "python_releaselevel": sys.version_info.releaselevel,
              "sqlite": sqlite3.sqlite_version, "openssl": ssl.OPENSSL_VERSION,
              "zlib": zlib.ZLIB_RUNTIME_VERSION, "packages": installed}
    try:
        from yaml import _yaml
        result["libyaml"] = _yaml.get_version_string()
    except ImportError:
        result["libyaml"] = None
    try:
        driver = Path(metadata.distribution("playwright").locate_file("playwright/driver/package/browsers.json"))
        result["playwright_browsers"] = json.loads(driver.read_text())["browsers"]
    except (metadata.PackageNotFoundError, OSError, KeyError):
        result["playwright_browsers"] = None
    return result


def markdown(report: dict) -> str:
    lines = ["# Technology release audit", "", f"Checked: {report['checked_at']}",
             f"Source commit: `{report['source_commit']}`", "",
             "Pinned versions are read from source. Reviewed versions are upstream baselines, not installed runtimes.",
             "Floating major Actions tags track patch/minor updates; their exact resolved SHA is runner evidence.", "",
             "| Technology | Pin / reviewed upstream | Latest stable | Status | Update route |",
             "|---|---|---|---|---|"]
    for row in report["releases"]:
        baseline = row.get("current", row.get("reviewed", "unknown"))
        lines.append(f"| [{row['name']}]({row['url']}) | {baseline} | {row.get('latest', 'unknown')} | {row['status']} | {row['owner']} |")
    lines += ["", "## This execution environment", "", "```json",
              json.dumps(report["environment"], indent=2), "```", "",
              "AVAILABLE: a newer transitive/tool release exists; pip resolves these under parent and Python constraints. Do not force an incompatible version.",
              "Use the saved JSON and pip freeze output for exact per-run resolution; hosts can differ.", "",
              "UPDATE: review and merge the Dependabot PR after all compatibility and browser checks pass.",
              "REVIEW: follow the owner route and migration checklist in docs/technology-inventory.md, then update the reviewed baseline.",
              "UNKNOWN: repair the lookup or unsupported version format; do not treat it as current.", "",
              "This audit does not install, merge, publish Pages, inspect private state, or update Replit."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".local/technology-audit")
    parser.add_argument("--fail-on-change", action="store_true")
    parser.add_argument("--environment-only", action="store_true")
    args = parser.parse_args()
    if args.environment_only:
        print(json.dumps(environment(), indent=2))
        return 0
    config = json.loads((ROOT / ".github/technology-watch.json").read_text())
    watches = discover(ROOT) + config["watches"]
    runtime = environment()
    for name in TRANSITIVE:
        installed = runtime["packages"][name]
        if installed:
            watches.append({"name": name, "kind": "pypi", "current": installed,
                            "url": f"https://pypi.org/pypi/{name}/json", "advisory": True,
                            "owner": "Parent package constraints and fresh pip resolution; pip itself is host tooling."})
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(check, watches))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                            capture_output=True, check=True).stdout.strip()
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "source_commit": commit,
              "releases": rows, "environment": runtime}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "report.md").write_text(markdown(report), encoding="utf-8")
    for row in rows:
        detail = f" ({row['error']})" if row.get("error") else ""
        print(f"{row['status']}: {row['name']} -> {row.get('latest', 'unknown')}{detail}")
    print(f"Reports: {args.output_dir}")
    if any(r["status"] == "UNKNOWN" for r in rows):
        return 2
    if args.fail_on_change and any(r["status"] in {"UPDATE", "REVIEW"} for r in rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
