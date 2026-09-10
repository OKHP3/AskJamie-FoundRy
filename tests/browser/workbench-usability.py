from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

from playwright.async_api import async_playwright

try:
    from browser_diagnostics import BrowserDiagnostics
except ModuleNotFoundError:
    from tests.browser.browser_diagnostics import BrowserDiagnostics


ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path(os.environ.get("FOUNDRY_PYTHON", sys.executable))
ARTIFACT_DIR = (
    Path(os.environ["BROWSER_ARTIFACTS_DIR"])
    if os.environ.get("BROWSER_ARTIFACTS_DIR")
    else None
)
BROWSER_EXECUTABLE = os.environ.get("BROWSER_EXECUTABLE_PATH")
DRAFT_FIELDS = [
    "title",
    "slug",
    "code",
    "family",
    "kind",
    "purpose",
    "audience",
    "source_text",
    "source_reference",
    "instructions",
    "output_contract",
    "constraints",
    "target",
    "phase",
    "evidence",
    "client_org",
    "parent_capability",
    "bfs_firewall",
    "visibility_lock",
    "skill_ids",
    "workflow_steps",
    "decision",
    "eval_cases",
]

def find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_health(port: int, timeout: float = 20.0) -> None:
    import urllib.request

    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/api/health"
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # pragma: no cover - best-effort readiness loop
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(f"Workbench did not become ready: {last_error}")


def put_json(port: int, path: str, payload: dict) -> None:
    import urllib.request

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data,
        method="PUT",
        headers={
            "Content-Type": "application/json",
            "X-Foundry-Request": "1",
            "Origin": f"http://127.0.0.1:{port}",
        },
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status != 200:  # pragma: no cover - defensive check
            raise RuntimeError(f"Unexpected status {response.status}")


async def main() -> None:
    port = find_free_port()
    diagnostics = BrowserDiagnostics()
    if ARTIFACT_DIR:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as data_dir:
        server = subprocess.Popen(
            [str(PYTHON), "-m", "workbench", "--port", str(port), "--data-dir", data_dir],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        browser = None
        page = None
        try:
            wait_for_health(port)
            async with async_playwright() as playwright:
                launch_options = (
                    {"executable_path": BROWSER_EXECUTABLE}
                    if BROWSER_EXECUTABLE
                    else {}
                )
                browser = await playwright.chromium.launch(**launch_options)

                async def load_with_delay(width: int, height: int):
                    context = await browser.new_context(viewport={"width": width, "height": height})
                    page = await context.new_page()
                    diagnostics.attach(page, f"loading-{width}x{height}")

                    async def slow_route(route):
                        await asyncio.sleep(0.75)
                        await route.continue_()

                    try:
                        await page.route("**/api/projects", slow_route)
                        await page.route("**/api/skills", slow_route)
                        await page.goto(f"http://127.0.0.1:{port}", wait_until="domcontentloaded")
                        await page.wait_for_timeout(150)
                        loading_text = await page.locator("body").inner_text()
                        assert "Loading saved work" in loading_text or "Getting the desk ready" in loading_text
                        await page.wait_for_load_state("networkidle")
                        metrics = await page.evaluate(
                            """() => ({
                                sw: document.documentElement.scrollWidth,
                                cw: document.documentElement.clientWidth,
                                sh: document.documentElement.scrollHeight,
                                ch: document.documentElement.clientHeight,
                            })"""
                        )
                        assert metrics["sw"] == metrics["cw"], metrics
                    except Exception:
                        if ARTIFACT_DIR:
                            await page.screenshot(
                                path=str(ARTIFACT_DIR / f"loading-{width}x{height}.png"),
                                full_page=True,
                            )
                        raise
                    finally:
                        await context.close()

                for size in [(1440, 900), (768, 900), (390, 844), (320, 568)]:
                    await load_with_delay(*size)

                context = await browser.new_context(viewport={"width": 1440, "height": 900})
                page = await context.new_page()
                diagnostics.attach(page, "workbench")
                await page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")

                async def navigate_with_confirmation(view: str, accept: bool) -> str:
                    prompt: dict[str, str] = {}

                    async def handle_dialog(dialog) -> None:
                        prompt["type"] = dialog.type
                        prompt["message"] = dialog.message
                        if accept:
                            await dialog.accept()
                        else:
                            await dialog.dismiss()

                    page.once("dialog", handle_dialog)
                    await page.locator(f"button.nav-item[data-view='{view}']").click()
                    assert prompt.get("type") == "confirm", prompt
                    assert (
                        prompt.get("message")
                        == "This project has unsaved changes. Leave without saving?"
                    ), prompt
                    return prompt["message"]

                focus_labels = []
                for _ in range(7):
                    await page.keyboard.press("Tab")
                    focus_labels.append(
                        await page.evaluate(
                            """() => {
                                const el = document.activeElement;
                                return [el.tagName, el.textContent.trim().slice(0, 40)].join("#");
                            }"""
                        )
                    )
                assert focus_labels[0].endswith("#⌂Workbench"), focus_labels
                assert any("Refresh" in item for item in focus_labels), focus_labels
                assert any("New project" in item for item in focus_labels), focus_labels

                await page.get_by_role("button", name="＋ New project").click()
                await page.get_by_role("radio", name="Blank capability").check()
                await page.get_by_role("button", name="Create draft").click()
                await page.wait_for_load_state("networkidle")
                await page.get_by_role("tab", name="Brief").click()
                await page.get_by_label("Title").fill("Usability check")
                await page.get_by_role("button", name="Save changes").click()
                await page.wait_for_selector(".success-box")
                await page.wait_for_timeout(150)
                success = await page.locator(".success-box").inner_text()
                assert "Saved. The desk has a new revision." in success
                status = await page.locator("#live-region").inner_text()
                assert "Project saved" in status or "Saved" in status

                project = await page.evaluate(
                    """async () => {
                        const response = await fetch('/api/projects');
                        const data = await response.json();
                        return data.projects[0];
                    }"""
                )
                project["title"] = "External update"
                put_json(
                    port,
                    f"/api/projects/{project['id']}",
                    {key: project[key] for key in DRAFT_FIELDS} | {"revision": project["revision"]},
                )

                await page.get_by_role("tab", name="Brief").click()
                await page.get_by_label("Title").fill("Local conflict")
                await page.get_by_role("button", name="Save changes").click()
                await page.wait_for_selector(".recovery-box")
                await page.wait_for_timeout(150)
                recovery = await page.locator(".recovery-box").inner_text()
                assert "Stale save detected" in recovery
                await page.get_by_role("button", name="Reload saved copy").click()
                await page.wait_for_load_state("networkidle")
                await page.get_by_label("Title").wait_for()
                title = await page.get_by_label("Title").input_value()
                assert title == "External update"

                await page.get_by_label("Title").fill("Unsaved draft stays safe")
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"

                await navigate_with_confirmation("workbench", accept=False)
                assert await page.locator("#view-title").inner_text() == "Saved capability projects"
                assert await page.get_by_label("Title").input_value() == "Unsaved draft stays safe"
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"

                await navigate_with_confirmation("workbench", accept=True)
                assert await page.locator("#view-title").inner_text() == "Your capability desk"
                assert not await page.get_by_label("Title").count()

                await navigate_with_confirmation("projects", accept=True)
                await page.get_by_label("Title").wait_for()
                assert await page.get_by_label("Title").input_value() == "Unsaved draft stays safe"
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"

                await page.get_by_role("button", name="Save changes").click()
                await page.get_by_text("Saved. The desk has a new revision.").wait_for()
                await page.locator(".save-state").filter(has_text="Saved locally").wait_for()
                page.once("dialog", lambda dialog: dialog.accept())
                await page.get_by_role("button", name="Duplicate").click()
                await page.get_by_text(
                    "Private copy created. Its evaluation history starts fresh."
                ).wait_for()
                await page.get_by_label("Title").wait_for()
                duplicate_title = await page.get_by_label("Title").input_value()
                assert duplicate_title == "Unsaved draft stays safe copy", duplicate_title
                page.once("dialog", lambda dialog: dialog.accept())
                await page.get_by_role("button", name="Delete").click()
                await page.get_by_text("The editor is waiting").wait_for()
                assert await page.locator(".editor").count() == 0
                assert await page.get_by_text("Saved capability projects").count() >= 1

                await context.close()
        except Exception:
            if ARTIFACT_DIR and page is not None:
                try:
                    await page.screenshot(
                        path=str(ARTIFACT_DIR / "workbench-usability-failure.png"),
                        full_page=True,
                    )
                except Exception:
                    pass
            if ARTIFACT_DIR:
                diagnostics.write(ARTIFACT_DIR)
            raise
        finally:
            if browser is not None:
                await browser.close()
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:  # pragma: no cover - cleanup
                server.kill()
            if ARTIFACT_DIR and server.stdout is not None:
                (ARTIFACT_DIR / "workbench-server.log").write_text(
                    server.stdout.read(),
                    encoding="utf-8",
                )


if __name__ == "__main__":
    asyncio.run(main())
