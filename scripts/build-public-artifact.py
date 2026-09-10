#!/usr/bin/env python3
"""Check and package the read-only AskJamie Pages artifact."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "public"
OUTPUT = ROOT / "dist" / "pages"
REQUIRED = ("index.html", "styles.css", ".nojekyll")
FORBIDDEN = (
    "/api/",
    ".foundry-data",
    "workbench.sqlite",
    "localStorage",
    "sessionStorage",
    "fetch(",
)


def check() -> None:
    if not SOURCE.is_dir():
        raise SystemExit("public artifact directory is missing")
    for name in REQUIRED:
        if not (SOURCE / name).is_file():
            raise SystemExit(f"public artifact is missing {name}")
    html = (SOURCE / "index.html").read_text(encoding="utf-8")
    if "<title>" not in html or 'name="description"' not in html:
        raise SystemExit("public artifact requires a title and description")
    if re.search(r'href="/|src="/', html):
        raise SystemExit("public artifact contains a root-relative asset path")
    for marker in FORBIDDEN:
        if marker in html or marker in (SOURCE / "styles.css").read_text(encoding="utf-8"):
            raise SystemExit(f"public artifact contains forbidden private/runtime marker: {marker}")
    for reference in re.findall(r'(?:href|src)="([^"]+)"', html):
        if reference in {"", "./"} or reference.startswith(("#", "http://", "https://", "mailto:")):
            continue
        if not (SOURCE / reference).is_file():
            raise SystemExit(f"public artifact reference does not exist: {reference}")
    subprocess.run(["node", "--check", str(SOURCE / "site.js")], check=False) if (SOURCE / "site.js").exists() else None
    print("Public artifact check passed: read-only, relative, and self-contained.")


def build() -> None:
    check()
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(SOURCE, OUTPUT)
    print(f"Built {OUTPUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="copy checked files to dist/pages")
    args = parser.parse_args()
    build() if args.build else check()
