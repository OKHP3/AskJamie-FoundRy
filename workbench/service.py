"""Workbench validation, evaluation, reference data, and package generation."""

from __future__ import annotations

import html
import hashlib
import io
import json
import re
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from .model import InputError, run_decision, validate_answer_nodes, validate_graph
from .store import Store, utc_now


ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "registry" / "index.yaml"
SKILLS_PATH = Path(__file__).resolve().parent / "data" / "skills.json"
TEMPLATE_PATH = ROOT / "_template"
MANIFEST_SCHEMA_PATH = ROOT / "schemas" / "manifest.schema.yaml"
REGISTRY_SCHEMA_PATH = ROOT / "schemas" / "registry.schema.yaml"
REQUIRED_EXPORT_FIELDS = (
    "title", "purpose", "audience", "source_text", "source_reference", "instructions", "output_contract"
)
TEMPLATE_MARKERS = re.compile(
    r"\[(?:PLACEHOLDER|DISPLAY_NAME|REPO_NAME|TYPE|capability-slug|aj##[^\]]*|core-capability[^\]]*|"
    r"draft[^\]]*|status|link or notes|specify)\]|YYYY-MM-DD|Template instruction",
    re.IGNORECASE,
)


def read_registry() -> dict[str, Any]:
    try:
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise RuntimeError(f"canonical registry is unavailable: {error}") from error
    repositories = data.get("repositories", []) if isinstance(data, dict) else []
    if not isinstance(repositories, list):
        raise RuntimeError("canonical registry has an invalid repositories value")
    return {
        "repositories": repositories,
        "note": "Read-only canonical registry metadata. Entries do not prove a remote repository exists or operates.",
    }


def read_skills() -> dict[str, Any]:
    empty = {
        "sourceRepository": "",
        "sourceCommit": "",
        "generatedAt": "",
        "retrievedAt": "",
        "skills": [],
    }
    try:
        data = json.loads(SKILLS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return empty
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"skill metadata snapshot is unavailable: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("skills"), list):
        raise RuntimeError("skill metadata snapshot has an invalid shape")
    metadata_fields = ("sourceRepository", "sourceCommit", "generatedAt", "retrievedAt")
    if any(not isinstance(data.get(field, ""), str) for field in metadata_fields):
        raise RuntimeError("skill metadata snapshot has invalid provenance fields")
    skill_fields = ("id", "name", "family", "description", "maturity", "evidenceStatus", "sourceUrl")
    seen: set[str] = set()
    for index, skill in enumerate(data["skills"]):
        if not isinstance(skill, dict) or any(not isinstance(skill.get(field), str) for field in skill_fields):
            raise RuntimeError(f"skill metadata snapshot entry {index} has an invalid shape")
        if not skill["id"] or skill["id"] in seen:
            raise RuntimeError(f"skill metadata snapshot entry {index} has a missing or duplicate ID")
        seen.add(skill["id"])
    return {**empty, **{key: data.get(key, empty[key]) for key in empty}}


def repo_name(project: dict[str, Any]) -> str:
    code, slug = project.get("code", ""), project.get("slug", "")
    if not code or not slug:
        return ""
    base = f"askjamie-{code}-{slug}"
    return f"{project['client_org']}-{base}" if project.get("client_org") else base


def validate_project(project: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in REQUIRED_EXPORT_FIELDS:
        if not project.get(field, "").strip():
            errors.append(f"{field} is required for export")
    if not project.get("slug"):
        errors.append("slug is required for export")
    if not project.get("code"):
        errors.append("code is required for export")
    if project.get("kind") == "decision-tool":
        errors.extend(validate_graph(project.get("decision")))
    if project.get("kind") == "workflow" and not any(step.strip() for step in project.get("workflow_steps", [])):
        errors.append("workflow_steps requires at least one nonempty step for workflow export")

    try:
        registry = read_registry()["repositories"]
    except RuntimeError as error:
        errors.append(str(error))
        registry = []
    code = project.get("code")
    family = project.get("family")
    if code and family == "client-overlay":
        candidates = [entry for entry in registry if entry.get("code") == code and entry.get("family") != "client-overlay"]
        parent = project.get("parent_capability")
        if not parent:
            errors.append("parent_capability is required for a client overlay")
        elif not any(parent in {entry.get("repo"), str(entry.get("repo", "")).removeprefix("OKHP3/")} for entry in candidates):
            errors.append("parent_capability must reference a governed non-client repository with the same code")
        generated_repo = f"OKHP3/{repo_name(project)}"
        if any(entry.get("repo") == generated_repo for entry in registry):
            errors.append(f"repository name conflicts with the canonical registry: {generated_repo}")
    elif code:
        generated_repo = f"OKHP3/{repo_name(project)}"
        if any(entry.get("code") == code or entry.get("repo") == generated_repo for entry in registry):
            errors.append(f"code or repository name conflicts with the canonical registry: {code}")

    try:
        skills = read_skills()
        known_skills = {item.get("id") for item in skills["skills"] if isinstance(item, dict)}
        missing = [skill_id for skill_id in project.get("skill_ids", []) if skill_id not in known_skills]
        if missing:
            errors.append(f"selected skill metadata is unavailable: {', '.join(missing)}")
        if not project.get("skill_ids"):
            warnings.append("no Skillz metadata is selected")
    except RuntimeError as error:
        if project.get("skill_ids"):
            errors.append(str(error))
        else:
            warnings.append(str(error))

    if not project.get("eval_cases"):
        warnings.append("evaluation suite is empty; no behavioral evidence will be produced")
    return {"valid": not errors, "errors": list(dict.fromkeys(errors)), "warnings": warnings, "repo": repo_name(project)}


def evaluate_project(project: dict[str, Any], store: Store) -> dict[str, Any]:
    cases: list[dict[str, str]] = []
    for index, case in enumerate(project["eval_cases"]):
        name = case.get("name", "").strip() or f"Case {index + 1}"
        if project["kind"] == "decision-tool":
            graph_errors = validate_graph(project["decision"])
            if graph_errors:
                status, detail = "unrun", f"Decision graph invalid: {'; '.join(graph_errors)}"
            elif not case.get("expected_result", "").strip():
                status, detail = "unrun", "Expected result is missing."
            else:
                try:
                    validate_answer_nodes(project["decision"], case.get("answers", {}))
                    outcome = run_decision(project["decision"], case.get("answers", {}))
                    if not outcome["complete"]:
                        status, detail = "unrun", f"Answers stop before node {outcome['next']['id']}."
                    elif outcome["result"] == case["expected_result"]:
                        status, detail = "passed", "Deterministic decision result matched exactly."
                    else:
                        status, detail = "failed", f"Expected {case['expected_result']!r}; received {outcome['result']!r}."
                except InputError as error:
                    status, detail = "unrun", f"Invalid decision answers: {error}"
        else:
            response = case.get("response", "")
            if not response.strip():
                status, detail = "unrun", "No supplied response. This evaluator does not call an AI."
            else:
                absent = [text for text in case.get("required", []) if text not in response]
                present = [text for text in case.get("forbidden", []) if text in response]
                if absent or present:
                    pieces = []
                    if absent:
                        pieces.append(f"missing required text: {', '.join(repr(item) for item in absent)}")
                    if present:
                        pieces.append(f"contains forbidden text: {', '.join(repr(item) for item in present)}")
                    status, detail = "failed", "Supplied-response checks failed: " + "; ".join(pieces) + "."
                else:
                    status, detail = "passed", "Supplied-response text checks passed; no AI was run."
        cases.append({"name": name, "status": status, "detail": detail})
    counts = {status: sum(case["status"] == status for case in cases) for status in ("passed", "failed", "unrun")}
    record = {
        "revision": project["revision"],
        **counts,
        "cases": cases,
        "evaluated_at": utc_now(),
    }
    store.save_evaluation(project["id"], record)
    return record


def _manifest(project: dict[str, Any]) -> dict[str, Any]:
    today = date.today().isoformat()
    visibility: dict[str, Any] = {"visibility": "private", "public_graduation_allowed": False}
    if project["client_org"]:
        visibility["client_org"] = project["client_org"]
    if project["visibility_lock"]:
        visibility["visibility_lock"] = project["visibility_lock"]
    if project["bfs_firewall"]:
        visibility["bfs_firewall"] = True
    lineage: dict[str, Any] = {
        "parent_foundry": "OKHP3/AskJamie-FoundRy",
        "parent_repo": "OKHP3/AskJamie-FoundRy",
    }
    if project["parent_capability"]:
        parent = project["parent_capability"]
        lineage["parent_capability"] = parent if parent.startswith("OKHP3/") else f"OKHP3/{parent}"
    return {
        "schema_version": "1.0",
        "identity": {
            "repo": f"OKHP3/{repo_name(project)}",
            "display_name": project["title"],
            "slug": project["slug"],
            "type": project["family"],
            "status": "draft",
        },
        "brand": {"brand_domain": "askjamie", "trademark": "AskJamie™", "capability_code": project["code"]},
        "lineage": lineage,
        "governance": {"naming_pattern": repo_name(project), "agents_doc": "AGENTS.md"},
        "deployment_surfaces": [
            {"name": name, "status": "none", "url": ""}
            for name in ("openai-custom-gpt", "microsoft-copilot", "gemini-gem")
        ],
        "visibility_control": visibility,
        "maintainers": [{"handle": "OKHP3", "role": "owner"}],
        "created": project["created_at"][:10] or today,
        "updated": today,
    }


def _selected_skills(project: dict[str, Any]) -> dict[str, Any]:
    snapshot = read_skills()
    selected = set(project["skill_ids"])
    return {**snapshot, "skills": [item for item in snapshot["skills"] if item.get("id") in selected]}


def _template_sha256() -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in TEMPLATE_PATH.rglob("*") if item.is_file() and item.name != "ABOUT.md"):
        digest.update(path.relative_to(TEMPLATE_PATH).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _decision_html(project: dict[str, Any]) -> str:
    graph_json = (json.dumps(project["decision"], ensure_ascii=False)
                  .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
                  .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    title = html.escape(project["title"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>body{{font:18px system-ui,sans-serif;max-width:48rem;margin:3rem auto;padding:1rem;color:#241f1c}}button{{margin:.5rem .5rem .5rem 0;padding:.7rem 1rem}}#result{{font-weight:700}}</style></head>
<body><main><h1>{title}</h1><p id="question"></p><div id="choices"><button data-answer="true">Yes</button><button data-answer="false">No</button></div><p id="result" role="status"></p><button id="restart">Restart</button></main>
<script>const graph={graph_json};const byId=Object.fromEntries(graph.nodes.map(n=>[n.id,n]));let current;
const question=document.getElementById('question'),choices=document.getElementById('choices'),result=document.getElementById('result');
function render(){{const node=byId[current];if(Object.prototype.hasOwnProperty.call(node,'result')){{question.textContent='';choices.hidden=true;result.textContent=node.result;}}else{{question.textContent=node.question;choices.hidden=false;result.textContent='';}}}}
function restart(){{current=graph.start;render();}}document.querySelectorAll('[data-answer]').forEach(button=>button.addEventListener('click',()=>{{const node=byId[current];current=button.dataset.answer==='true'?node.yes:node.no;render();}}));document.getElementById('restart').addEventListener('click',restart);restart();</script></body></html>"""


def _generated_files(project: dict[str, Any], store: Store) -> dict[str, bytes]:
    repo = repo_name(project)
    manifest = _manifest(project)
    schema = yaml.safe_load(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(manifest)
    except jsonschema.ValidationError as error:
        raise RuntimeError(f"generated manifest failed schema validation: {error.message}") from error
    selected_skills = _selected_skills(project)
    exported_at = utc_now()
    source_sha256 = hashlib.sha256(project["source_text"].encode("utf-8")).hexdigest()
    template_sha256 = _template_sha256()
    constraints = project["constraints"].strip() or "No additional constraints recorded."
    workflow = "\n".join(f"{index}. [ ] {step}" for index, step in enumerate(project["workflow_steps"], 1)) or "No workflow checklist applies."
    decision_usage = " For a decision tool, open `index.html` directly in a browser to run it offline." if project["kind"] == "decision-tool" else ""
    canonical_parent = project["parent_capability"]
    if canonical_parent and not canonical_parent.startswith("OKHP3/"):
        canonical_parent = f"OKHP3/{canonical_parent}"
    registry_entry = {
        "repo": f"OKHP3/{repo}", "display_name": project["title"], "code": project["code"],
        "family": project["family"], "status": "draft", "visibility": "private",
        "public_graduation_allowed": False,
        **({"parent_capability": canonical_parent} if canonical_parent else {}),
        **({"client_org": project["client_org"]} if project["client_org"] else {}),
        **({"visibility_lock": project["visibility_lock"]} if project["visibility_lock"] else {}),
        **({"bfs_firewall": True} if project["bfs_firewall"] else {}),
    }
    registry_schema = yaml.safe_load(REGISTRY_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(registry_schema["properties"]["repositories"]["items"]).validate(registry_entry)
    except jsonschema.ValidationError as error:
        raise RuntimeError(f"generated registry proposal failed schema validation: {error.message}") from error
    if registry_entry["visibility"] != "private" or registry_entry["public_graduation_allowed"]:
        raise RuntimeError("generated registry proposal violates private-draft controls")
    if project["visibility_lock"] and registry_entry.get("visibility_lock") != "permanent-private":
        raise RuntimeError("generated registry proposal lost permanent-private protection")
    files: dict[str, str] = {
        "README.md": f"# {project['title']}\n\n{project['purpose']}\n\n## Capability overview\n\n- Code: `{project['code']}`\n- Family: `{project['family']}`\n- Kind: `{project['kind']}`\n- Status: `draft`\n- Visibility: `private`\n- Parent FoundRy: `OKHP3/AskJamie-FoundRy`\n\n## Audience\n\n{project['audience']}\n\n## Use\n\nRead `skill/instructions.md` and `prompts/system.md`. Review recorded evidence in `tests/evals.json` and `exports/evaluation-records.json`.{decision_usage} This private draft package does not publish or provision a hosted assistant.\n\n## Repository structure\n\n`docs/` contains specifications, `origin/` preserves source, `skill/` and `prompts/` contain behavior, `research/` retains selected public Skillz metadata, `tests/` and `exports/` carry evidence, and `schemas/`, `assets/`, and `archive/` are reserved by the canonical scaffold.\n\n## Governance\n\nThis repository is governed by `OKHP3/AskJamie-FoundRy`. Contributors and agents must follow `AGENTS.md`.\n\n## Provenance\n\nGenerated from the canonical `OKHP3/AskJamie-FoundRy` `_template/` layout at {exported_at}, from project revision {project['revision']}. Template tree SHA-256: `{template_sha256}`. Original material is retained in `origin/source.md`; its SHA-256 is `{source_sha256}`.\n",
        "AGENTS.md": f"# AGENTS.md: {repo}\n\n## 0. Role\n\nThis repository is a private draft `{project['family']}` capability within the AskJamie ecosystem, governed by `OKHP3/AskJamie-FoundRy`.\n\n## 1. Authority chain\n\n`OKHP3/OverKill-Hill` -> `OKHP3/AskJamie-FoundRy` -> `OKHP3/{repo}`\n\n## 2. Repository purpose\n\n{project['purpose']}\n\n## 3. Lineage\n\n- Parent FoundRy: `OKHP3/AskJamie-FoundRy`\n- Capability code: `{project['code']}`\n- Capability slug: `{project['slug']}`\n- Full name: `{repo}`\n\n## 4. Directory contract\n\n- `docs/`: design notes and governance\n- `origin/`: raw source material\n- `skill/`: refined capability artifacts\n- `prompts/`: versioned prompts\n- `research/`: supporting references\n- `tests/`: evaluation and regression cases\n- `schemas/`: local schemas\n- `assets/`: local assets\n- `exports/`: generated exports and evidence\n- `archive/`: retired material\n\n## 5. Required files\n\nMaintain `AGENTS.md`, `README.md`, `CHANGELOG.md`, `LICENSE.md`, and `manifest.yaml`.\n\n## 6. Agent behavior\n\nPreserve the manifest lineage and private visibility. Never commingle client-sensitive content with public portfolio artifacts. Update the manifest when status or scope changes. Treat `bfs_firewall` and `visibility_lock: permanent-private` as confidential controls. Refer to the parent relay for naming, schema, and governance guidance.\n\n## 7. Deployment surfaces\n\nNo hosted deployment surface is activated by this draft package. Any future deployment requires separate review and authorization.\n\n## 8. Canonical principle\n\nThe durable asset is the capability and knowledge architecture in this repository. A platform-specific deployment is ephemeral by comparison.\n",
        "CHANGELOG.md": f"# Changelog\n\n## 0.1.0: {date.today().isoformat()}\n\n- Generated private draft package from AskJamie Found-Ry workbench project revision {project['revision']}.\n",
        "manifest.yaml": yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        "origin/source.md": f"# Source material\n\n## Reference\n\n{project['source_reference']}\n\n## Original text\n\n{project['source_text']}\n",
        "skill/instructions.md": f"# {project['title']}: instructions\n\n{project['instructions']}\n\n## Output contract\n\n{project['output_contract']}\n\n## Constraints\n\n{constraints}\n",
        "prompts/system.md": f"# System prompt\n\n{project['instructions']}\n\nFollow this output contract:\n\n{project['output_contract']}\n\nConstraints:\n\n{constraints}\n",
        "docs/specification.md": f"# Specification\n\n## Purpose\n\n{project['purpose']}\n\n## Audience\n\n{project['audience']}\n\n## Kind\n\n{project['kind']}\n\n## Ordered workflow checklist\n\n{workflow}\n",
        "tests/evals.json": json.dumps(project["eval_cases"], ensure_ascii=False, indent=2) + "\n",
        "exports/project.json": json.dumps(project, ensure_ascii=False, indent=2) + "\n",
        "exports/registry-proposal.yaml": yaml.safe_dump({
            "status": "pending", "applied": False, "note": "Proposal only. Not applied to the canonical registry.",
            "repository": registry_entry,
        }, sort_keys=False, allow_unicode=True),
        "research/skills.json": json.dumps(selected_skills, ensure_ascii=False, indent=2) + "\n",
        "exports/evaluation-records.json": json.dumps({"project_revision": project["revision"], "evaluations": store.evaluations(project["id"])}, ensure_ascii=False, indent=2) + "\n",
    }
    if project["kind"] == "decision-tool":
        files["decision.json"] = json.dumps(project["decision"], ensure_ascii=False, indent=2) + "\n"
        files["index.html"] = _decision_html(project)
    for path, content in files.items():
        if path in {"README.md", "AGENTS.md", "CHANGELOG.md", "manifest.yaml"} and TEMPLATE_MARKERS.search(content):
            raise RuntimeError(f"generated template document still contains a placeholder: {path}")
    return {path: content.encode("utf-8") for path, content in files.items()}


def export_project(project: dict[str, Any], store: Store) -> tuple[str, bytes]:
    result = validate_project(project)
    if not result["valid"]:
        raise InputError("Export blocked: " + "; ".join(result["errors"]))
    generated = _generated_files(project, store)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for directory in sorted(path.name for path in TEMPLATE_PATH.iterdir() if path.is_dir()):
            archive.writestr(f"{directory}/", b"")
        license_path = TEMPLATE_PATH / "LICENSE.md"
        archive.writestr("LICENSE.md", license_path.read_bytes())
        for path, content in sorted(generated.items()):
            archive.writestr(path, content)
    return f"{repo_name(project)}.zip", buffer.getvalue()
