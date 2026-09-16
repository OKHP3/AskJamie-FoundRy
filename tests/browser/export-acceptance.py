from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

try:
    from browser_diagnostics import BrowserDiagnostics, validate_jsonl_outputs
except ModuleNotFoundError:
    from tests.browser.browser_diagnostics import BrowserDiagnostics, validate_jsonl_outputs


ARTIFACT_DIR = Path(os.environ["BROWSER_ARTIFACTS_DIR"])
BROWSER_EXECUTABLE = os.environ.get("BROWSER_EXECUTABLE_PATH")
CONTROLLED_FAILURE = os.environ.get("BROWSER_CONTROLLED_FAILURE") == "export"


async def main() -> None:
    diagnostics = BrowserDiagnostics()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        launch_options = (
            {"executable_path": BROWSER_EXECUTABLE}
            if BROWSER_EXECUTABLE
            else {}
        )
        browser = await playwright.chromium.launch(**launch_options)
        page = await browser.new_page()
        diagnostics.attach(page, "export-runner")
        try:
            await page.goto(
                "http://127.0.0.1:8767/index.html",
                wait_until="networkidle",
            )
            if CONTROLLED_FAILURE:
                raise AssertionError("Controlled export browser assertion failure")
            assert await page.get_by_role("button", name="Yes").is_visible()
            assert await page.get_by_role("button", name="No").is_visible()
            assert await page.get_by_role("button", name="Restart").is_visible()
            await page.get_by_role("button", name="Yes").click()
            result = await page.locator("#result").inner_text()
            assert "<img src=x onerror=alert(1)>" in result
            assert await page.locator("img").count() == 0
            await page.get_by_role("button", name="Restart").click()
            assert await page.locator("#question").inner_text() == "Is the request clear?"
        except Exception:
            try:
                await page.screenshot(
                    path=str(ARTIFACT_DIR / "export-failure.png"),
                    full_page=True,
                )
            except Exception:
                pass
            diagnostics.write(
                ARTIFACT_DIR,
                check_name="Exported decision",
                file_prefix="export",
            )
            validate_jsonl_outputs(ARTIFACT_DIR, file_prefix="export")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AssertionError as error:
        print(error, file=sys.stderr)
        raise