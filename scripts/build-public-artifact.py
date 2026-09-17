#!/usr/bin/env python3
"""Check and package the read-only AskJamie Pages artifact."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
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
EXPECTED_PAGES_PATH = "/AskJamie-FoundRy/"
LIVE_REQUIRED_MARKERS = (
    "<title>AskJamie FoundRy | A careful place to shape capability</title>",
    "PUBLIC ORIENTATION / PRIVATE FABRICATION",
    "This page is read-only.",
    "loopback-only local",
    "no draft or private database is loaded here.",
    "Read-only orientation",
)
LIVE_EXTERNAL_LINKS = (
    "https://askjamie.bot/",
    "https://github.com/OKHP3/AskJamie",
    "https://github.com/OKHP3/AskJamie-FoundRy",
    "https://github.com/OKHP3/OverKill-Hill",
    "https://github.com/OKHP3/OverKill-Hill-FoundRy",
    "https://github.com/OKHP3/Glee-fullyTools-FoundRy",
    "https://okhp3.github.io/skillz/",
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


def normalized_path(url: str) -> str:
    """Normalize a Pages path while preserving the root path."""

    path = urlparse(url).path or "/"
    return path if path == "/" else f"{path.rstrip('/')}/"


def check_live(page_url: str) -> None:
    """Verify the deployed Pages URL serves the intended public artifact."""

    requested = urlparse(page_url)
    if requested.scheme not in {"http", "https"} or not requested.netloc:
        raise SystemExit(f"live Pages check failed: invalid page URL: {page_url}")
    if normalized_path(page_url) != EXPECTED_PAGES_PATH:
        raise SystemExit(
            "live Pages check failed: deployed repository subpath is wrong; "
            f"expected {EXPECTED_PAGES_PATH!r}, got {normalized_path(page_url)!r}"
        )

    request = Request(
        page_url,
        headers={
            "Cache-Control": "no-cache",
            "User-Agent": "AskJamie-FoundRy-pages-smoke-test",
        },
    )
    failure = None
    for attempt in range(5):
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
                final_url = response.geturl()
                html = response.read().decode("utf-8", errors="replace")
            failure = None
            break
        except HTTPError as error:
            failure = (
                "live Pages check failed: "
                f"{page_url} returned HTTP {error.code} instead of HTTP 200"
            )
        except URLError as error:
            failure = f"live Pages check failed: could not fetch {page_url}: {error.reason}"
        except TimeoutError:
            failure = f"live Pages check failed: timed out fetching {page_url}"
        if attempt < 4:
            time.sleep(2)
    if failure:
        raise SystemExit(failure)

    if status != 200:
        raise SystemExit(
            f"live Pages check failed: {page_url} returned HTTP {status} instead of HTTP 200"
        )
    if normalized_path(final_url) != EXPECTED_PAGES_PATH:
        raise SystemExit(
            "live Pages check failed: deployed URL redirected to the wrong "
            f"repository subpath; expected {EXPECTED_PAGES_PATH!r}, "
            f"got {normalized_path(final_url)!r}"
        )

    missing = [marker for marker in LIVE_REQUIRED_MARKERS if marker not in html]
    if missing:
        raise SystemExit(
            "live Pages check failed: deployed content is missing expected "
            f"public marker(s): {', '.join(missing)}"
        )
    missing_links = [
        link for link in LIVE_EXTERNAL_LINKS if f'href="{link}"' not in html
    ]
    if missing_links:
        raise SystemExit(
            "live Pages check failed: deployed content is missing expected "
            f"external link(s): {', '.join(missing_links)}"
        )
    for marker in FORBIDDEN:
        if marker in html:
            raise SystemExit(
                "live Pages check failed: deployed content contains forbidden "
                f"private/runtime marker: {marker}"
            )
    print(
        "Live Pages check passed: HTTP 200, expected repository subpath, "
        "public orientation markers, and external links verified."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="copy checked files to dist/pages")
    parser.add_argument(
        "--check-live",
        metavar="PAGE_URL",
        help="fetch and verify the deployed Pages URL",
    )
    args = parser.parse_args()
    if args.check_live:
        check_live(args.check_live)
    elif args.build:
        build()
    else:
        check()
