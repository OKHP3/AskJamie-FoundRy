from __future__ import annotations

import asyncio
import json
import os
import re
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
CONTROLLED_FAILURE = os.environ.get("BROWSER_CONTROLLED_FAILURE") == "workbench"
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
        browser_profile = Path(data_dir) / "browser-profile"
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

                await browser.close()
                browser = None
                context = await playwright.chromium.launch_persistent_context(
                    browser_profile,
                    viewport={"width": 1440, "height": 900},
                    **launch_options,
                )
                browser = context.browser
                page = await context.new_page()
                diagnostics.attach(page, "workbench")
                await page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
                if CONTROLLED_FAILURE:
                    raise AssertionError("Controlled workbench browser assertion failure")

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

                newer_saved = await page.evaluate(
                    """async () => {
                        const response = await fetch('/api/projects');
                        const data = await response.json();
                        return data.projects[0];
                    }"""
                )
                newer_saved["title"] = "Newer saved work"
                put_json(
                    port,
                    f"/api/projects/{newer_saved['id']}",
                    {key: newer_saved[key] for key in DRAFT_FIELDS}
                    | {"revision": newer_saved["revision"]},
                )

                refresh_prompt: dict[str, str] = {}

                async def accept_refresh(dialog) -> None:
                    refresh_prompt["type"] = dialog.type
                    await dialog.accept()

                page.once("dialog", accept_refresh)
                await page.reload(wait_until="networkidle")
                assert refresh_prompt.get("type") == "beforeunload", refresh_prompt
                await page.get_by_text("Local drafts found").wait_for()
                assert await page.get_by_role("button", name="Restore local draft").count() == 1
                saved_title = await page.evaluate(
                    """async () => (await (await fetch('/api/projects')).json()).projects[0].title"""
                )
                assert saved_title == "Newer saved work", saved_title

                await page.get_by_role("button", name="Restore local draft").click()
                await page.get_by_label("Title").wait_for()
                assert await page.get_by_label("Title").input_value() == "Unsaved draft stays safe"
                editor_recovery = page.locator(".editor .local-recovery-box")
                assert await editor_recovery.count() == 1
                recovery = await editor_recovery.inner_text()
                assert "based on an older revision" in recovery
                assert "Saved revision" in recovery
                assert "local base revision" in recovery
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"
                assert await page.get_by_role("button", name="Save changes").is_disabled()
                saved_title = await page.evaluate(
                    """async () => (await (await fetch('/api/projects')).json()).projects[0].title"""
                )
                assert saved_title == "Newer saved work", saved_title

                await page.get_by_role(
                    "button", name="Use recovered draft as next revision"
                ).click()
                assert await page.get_by_role("button", name="Save changes").is_enabled()
                saved_title = await page.evaluate(
                    """async () => (await (await fetch('/api/projects')).json()).projects[0].title"""
                )
                assert saved_title == "Newer saved work", saved_title
                await page.get_by_role("button", name="Save changes").click()
                await page.get_by_text("Saved. The desk has a new revision.").wait_for()
                await page.locator(".save-state").filter(has_text="Saved locally").wait_for()
                await page.get_by_label("Title").fill("Discarded local draft")
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"

                await context.close()
                browser = None
                context = await playwright.chromium.launch_persistent_context(
                    browser_profile,
                    viewport={"width": 1440, "height": 900},
                    **launch_options,
                )
                browser = context.browser
                page = await context.new_page()
                diagnostics.attach(page, "reopened-workbench")
                await page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
                await page.get_by_text("Local drafts found").wait_for()
                assert await page.get_by_role("button", name="Restore local draft").count() == 1
                saved_title = await page.evaluate(
                    """async () => (await (await fetch('/api/projects')).json()).projects[0].title"""
                )
                assert saved_title == "Unsaved draft stays safe", saved_title
                await page.get_by_role("button", name="Discard local draft").click()
                assert await page.get_by_text("Local drafts found").count() == 0
                saved_title = await page.evaluate(
                    """async () => (await (await fetch('/api/projects')).json()).projects[0].title"""
                )
                assert saved_title == "Unsaved draft stays safe", saved_title
                await page.locator(".project-row").first.click()
                await page.get_by_label("Title").wait_for()
                assert await page.get_by_label("Title").input_value() == "Unsaved draft stays safe"

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
                duplicate_title = (
                    "Unsaved draft stays safe copy — a long / unusual destination title "
                    "with extra context " * 5
                )
                await page.get_by_label("Title").fill(duplicate_title)
                await page.get_by_role("button", name="Save changes").click()
                await page.get_by_text("Saved. The desk has a new revision.").wait_for()
                await page.locator(".save-state").filter(has_text="Saved locally").wait_for()

                original_row = page.locator(".project-row").filter(
                    has=page.locator(
                        "strong", has_text=re.compile(r"^Unsaved draft stays safe$")
                    )
                )
                duplicate_row = page.locator(".project-row").filter(
                    has=page.locator(
                        "strong",
                        has_text=re.compile(rf"^{re.escape(duplicate_title)}$"),
                    )
                )
                await original_row.click()
                await page.get_by_label("Title").wait_for()
                assert await page.get_by_label("Title").input_value() == "Unsaved draft stays safe"
                await page.get_by_label("Title").fill("Unsaved original remains")
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"

                assert await original_row.count() == 1
                assert await duplicate_row.count() == 1
                switch_prompt: dict[str, str] = {}

                async def dismiss_project_switch(dialog) -> None:
                    switch_prompt["type"] = dialog.type
                    switch_prompt["message"] = dialog.message
                    await dialog.dismiss()

                page.once("dialog", dismiss_project_switch)
                await duplicate_row.click()
                assert switch_prompt.get("type") == "confirm", switch_prompt
                switch_message = switch_prompt.get("message", "")
                assert switch_message.startswith(
                    "This project has unsaved changes. Leave without saving and open “"
                ), switch_prompt
                assert duplicate_title[:50] in switch_message, switch_prompt
                assert len(switch_message) < 220, switch_prompt
                assert "\n" not in switch_message, switch_prompt
                assert await page.get_by_label("Title").input_value() == "Unsaved original remains"
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"
                saved_titles = await page.evaluate(
                    """async () => (await (await fetch('/api/projects')).json()).projects.map((item) => item.title)"""
                )
                assert "Unsaved original remains" not in saved_titles, saved_titles
                assert duplicate_title in saved_titles, saved_titles

                page.once("dialog", lambda dialog: dialog.accept())
                await duplicate_row.click()
                await page.get_by_label("Title").wait_for()
                assert await page.get_by_label("Title").input_value() == duplicate_title
                assert await page.locator(".save-state").inner_text() == "Saved locally"
                await page.get_by_label("Title").fill("Unsaved duplicate remains")
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"

                race_projects = await page.evaluate(
                    """async () => {
                        const data = await (await fetch('/api/projects')).json();
                        return Object.fromEntries(
                            data.projects.map((item) => [
                                item.id,
                                { title: item.title, revision: item.revision },
                            ]),
                        );
                    }"""
                )
                original_id = next(
                    project_id
                    for project_id, item in race_projects.items()
                    if item["title"] == "Unsaved draft stays safe"
                )
                duplicate_id = next(
                    project_id
                    for project_id, item in race_projects.items()
                    if item["title"] == duplicate_title
                )
                delayed_project_path = f"/api/projects/{original_id}"
                delayed_request = {"seen": False}

                async def delay_first_project(route) -> None:
                    if route.request.url.endswith(delayed_project_path):
                        delayed_request["seen"] = True
                        await asyncio.sleep(0.75)
                    await route.continue_()

                await page.route("**/api/projects/*", delay_first_project)
                race_prompts: list[str] = []

                async def accept_race_dialog(dialog) -> None:
                    race_prompts.append(dialog.message)
                    await dialog.accept()

                page.once("dialog", accept_race_dialog)
                await original_row.click()
                page.once("dialog", accept_race_dialog)
                await duplicate_row.click()
                await page.wait_for_function(
                    """expected => document.querySelector("#field-title")?.value === expected""",
                    arg=duplicate_title,
                )
                assert delayed_request["seen"]
                assert len(race_prompts) == 2, race_prompts
                assert "Unsaved draft stays safe" in race_prompts[0], race_prompts
                assert duplicate_title[:50] in race_prompts[1], race_prompts
                assert await page.get_by_label("Title").input_value() == duplicate_title
                assert (
                    f"revision {race_projects[duplicate_id]['revision']}"
                    in await page.locator(".editor-head p").inner_text()
                )
                await page.unroute("**/api/projects/*", delay_first_project)

                matching_saved_title = "Matching saved project title"
                await page.evaluate(
                    """async ({ projectIds, title, draftFields }) => {
                        for (const projectId of projectIds) {
                            const project = await (
                                await fetch(`/api/projects/${encodeURIComponent(projectId)}`)
                            ).json();
                            const draft = Object.fromEntries(
                                draftFields.map((field) => [field, project[field]])
                            );
                            const response = await fetch(
                                `/api/projects/${encodeURIComponent(projectId)}`,
                                {
                                    method: "PUT",
                                    headers: {
                                        "Content-Type": "application/json",
                                        "X-Foundry-Request": "1",
                                    },
                                    body: JSON.stringify({
                                        ...draft,
                                        title,
                                        revision: project.revision,
                                    }),
                                },
                            );
                            if (!response.ok) throw new Error(await response.text());
                        }
                    }""",
                    {
                        "projectIds": [original_id, duplicate_id],
                        "title": matching_saved_title,
                        "draftFields": DRAFT_FIELDS,
                    },
                )
                saved_before_reopen = await page.evaluate(
                    """async () => {
                        const data = await (await fetch('/api/projects')).json();
                        return Object.fromEntries(
                            data.projects.map((item) => [
                                item.id,
                                { title: item.title, revision: item.revision },
                            ]),
                        );
                    }"""
                )
                assert sorted(
                    item["title"] for item in saved_before_reopen.values()
                ) == [
                    matching_saved_title,
                    matching_saved_title,
                ], saved_before_reopen

                await context.close()
                browser = None
                context = await playwright.chromium.launch_persistent_context(
                    browser_profile,
                    viewport={"width": 1440, "height": 900},
                    **launch_options,
                )
                browser = context.browser
                page = await context.new_page()
                diagnostics.attach(page, "reopened-multiple-drafts")
                await page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
                await page.get_by_text("Local drafts found").wait_for()

                original_recovery = page.locator(".local-recovery-item").filter(
                    has=page.locator(
                        "strong", has_text=re.compile(r"^Unsaved original remains$")
                    )
                )
                duplicate_recovery = page.locator(".local-recovery-item").filter(
                    has=page.locator(
                        "strong", has_text=re.compile(r"^Unsaved duplicate remains$")
                    )
                )
                assert await original_recovery.count() == 1
                assert await duplicate_recovery.count() == 1
                assert (
                    await original_recovery.get_attribute("data-project-id")
                    == original_id
                )
                assert (
                    await duplicate_recovery.get_attribute("data-project-id")
                    == duplicate_id
                )
                assert (
                    f"Saved project: {matching_saved_title} · ID {original_id}"
                    in await original_recovery.inner_text()
                )
                assert (
                    f"Saved project: {matching_saved_title} · ID {duplicate_id}"
                    in await duplicate_recovery.inner_text()
                )

                await original_recovery.get_by_role(
                    "button", name="Discard local draft"
                ).click()
                assert await original_recovery.count() == 0
                assert await duplicate_recovery.count() == 1
                assert await page.get_by_role(
                    "button", name="Restore local draft"
                ).count() == 1
                saved_after_discard = await page.evaluate(
                    """async () => {
                        const data = await (await fetch('/api/projects')).json();
                        return Object.fromEntries(
                            data.projects.map((item) => [
                                item.id,
                                { title: item.title, revision: item.revision },
                            ]),
                        );
                    }"""
                )
                assert saved_after_discard == saved_before_reopen, (
                    saved_before_reopen,
                    saved_after_discard,
                )

                await duplicate_recovery.get_by_role(
                    "button", name="Restore local draft"
                ).click()
                await page.get_by_label("Title").wait_for()
                assert (
                    await page.get_by_label("Title").input_value()
                    == "Unsaved duplicate remains"
                )
                assert await page.locator(".save-state").inner_text() == "Unsaved changes"
                saved_after_restore = await page.evaluate(
                    """async () => {
                        const data = await (await fetch('/api/projects')).json();
                        return Object.fromEntries(
                            data.projects.map((item) => [
                                item.id,
                                { title: item.title, revision: item.revision },
                            ]),
                        );
                    }"""
                )
                assert saved_after_restore == saved_before_reopen, (
                    saved_before_reopen,
                    saved_after_restore,
                )

                await page.locator(".editor .local-recovery-box").get_by_role(
                    "button", name="Discard local draft"
                ).click()
                await page.get_by_label("Title").wait_for()
                assert (
                    await page.get_by_label("Title").input_value()
                    == matching_saved_title
                )
                assert await page.locator(".save-state").inner_text() == "Saved locally"

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
                diagnostics.write(
                    ARTIFACT_DIR,
                    check_name="Workbench usability",
                    file_prefix="workbench",
                )
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
