"""Draft normalization and validation for workbench projects."""

from __future__ import annotations

import re
import math
from typing import Any


DRAFT_FIELDS = {
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
    "client_org",
    "parent_capability",
    "bfs_firewall",
    "visibility_lock",
    "skill_ids",
    "workflow_steps",
    "decision",
    "eval_cases",
}

FAMILIES = {
    "core-capability",
    "brandguard",
    "enterprise-sleuth",
    "client-overlay",
    "conversation-design",
    "rag-experiment",
}
KINDS = {"assistant", "decision-tool", "workflow"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CODE_RE = re.compile(r"^(?:aj(?:0[1-9]|[1-9][0-9])|brg[0-9]{2})$")
NODE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_TEXT = 512_000
MAX_SHORT = 4_000
MAX_ITEMS = 1_000


class InputError(ValueError):
    """Client input is invalid."""


def default_draft() -> dict[str, Any]:
    return {
        "title": "",
        "slug": "",
        "code": "aj05",
        "family": "core-capability",
        "kind": "assistant",
        "purpose": "",
        "audience": "",
        "source_text": "",
        "source_reference": "",
        "instructions": "",
        "output_contract": "",
        "constraints": "",
        "client_org": "",
        "parent_capability": "",
        "bfs_firewall": False,
        "visibility_lock": "",
        "skill_ids": [],
        "workflow_steps": [],
        "decision": {},
        "eval_cases": [],
    }


def _clean_text(value: Any, field: str, limit: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise InputError(f"{field} must be a string")
    if len(value) > limit:
        raise InputError(f"{field} exceeds {limit} characters")
    if "\x00" in value:
        raise InputError(f"{field} contains a prohibited null character")
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise InputError(f"{field} must be an array")
    if len(value) > MAX_ITEMS:
        raise InputError(f"{field} exceeds {MAX_ITEMS} items")
    return [_clean_text(item, f"{field}[{index}]", MAX_SHORT) for index, item in enumerate(value)]


def normalize_draft(raw: Any, *, allow_revision: bool = False) -> tuple[dict[str, Any], int | None]:
    if not isinstance(raw, dict):
        raise InputError("request body must be a JSON object")
    allowed = DRAFT_FIELDS | ({"revision"} if allow_revision else set())
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise InputError(f"unknown field(s): {', '.join(unknown)}")
    revision = raw.get("revision") if allow_revision else None
    if allow_revision and (isinstance(revision, bool) or not isinstance(revision, int) or revision < 1):
        raise InputError("revision must be a positive integer")

    draft = default_draft()
    draft.update({key: value for key, value in raw.items() if key in DRAFT_FIELDS})
    short_fields = {
        "title", "slug", "code", "family", "kind", "purpose", "audience",
        "source_reference", "client_org", "parent_capability", "visibility_lock",
    }
    for field in DRAFT_FIELDS - {"bfs_firewall", "skill_ids", "workflow_steps", "decision", "eval_cases"}:
        draft[field] = _clean_text(draft[field], field, MAX_SHORT if field in short_fields else MAX_TEXT)
    if draft["family"] not in FAMILIES:
        raise InputError(f"family must be one of: {', '.join(sorted(FAMILIES))}")
    if draft["kind"] not in KINDS:
        raise InputError(f"kind must be one of: {', '.join(sorted(KINDS))}")
    if draft["code"] and not CODE_RE.fullmatch(draft["code"]):
        raise InputError("code must be aj01-aj99 or brg00-brg99")
    for field in ("slug", "client_org"):
        if draft[field] and not SLUG_RE.fullmatch(draft[field]):
            raise InputError(f"{field} must use ASCII lowercase letters, digits, and single interior hyphens")
    if not isinstance(draft["bfs_firewall"], bool):
        raise InputError("bfs_firewall must be a boolean")
    if draft["visibility_lock"] not in {"", "permanent-private"}:
        raise InputError("visibility_lock must be empty or permanent-private")
    if draft["client_org"] and draft["family"] != "client-overlay":
        raise InputError("client_org requires client-overlay family")
    draft["skill_ids"] = _string_list(draft["skill_ids"], "skill_ids")
    draft["workflow_steps"] = _string_list(draft["workflow_steps"], "workflow_steps")
    if len(set(draft["skill_ids"])) != len(draft["skill_ids"]):
        raise InputError("skill_ids must not contain duplicates")
    if not isinstance(draft["decision"], dict):
        raise InputError("decision must be an object")
    if not isinstance(draft["eval_cases"], list):
        raise InputError("eval_cases must be an array")
    if len(draft["eval_cases"]) > MAX_ITEMS:
        raise InputError(f"eval_cases exceeds {MAX_ITEMS} items")
    _check_json_shape(draft["decision"], "decision")
    _check_json_shape(draft["eval_cases"], "eval_cases")
    _validate_eval_case_types(draft["eval_cases"], draft["kind"])

    if draft["client_org"] or draft["family"] == "client-overlay" or draft["bfs_firewall"] or draft["visibility_lock"]:
        draft["visibility_lock"] = "permanent-private"
    return draft, revision


def _validate_eval_case_types(cases: list[Any], kind: str) -> None:
    fields = {"name", "answers", "expected_result"} if kind == "decision-tool" else {
        "name", "input", "response", "required", "forbidden"
    }
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise InputError(f"eval_cases[{index}] must be an object")
        unknown = sorted(set(case) - fields)
        if unknown:
            raise InputError(f"eval_cases[{index}] has unknown field(s): {', '.join(unknown)}")
        for field in fields - {"answers", "required", "forbidden"}:
            if field in case:
                _clean_text(case[field], f"eval_cases[{index}].{field}", MAX_TEXT)
        if kind == "decision-tool":
            answers = case.get("answers", {})
            if not isinstance(answers, dict):
                raise InputError(f"eval_cases[{index}].answers must be an object")
            for node_id, answer in answers.items():
                if not isinstance(node_id, str) or not NODE_RE.fullmatch(node_id) or not isinstance(answer, bool):
                    raise InputError(f"eval_cases[{index}].answers must map valid node IDs to booleans")
        else:
            for field in ("required", "forbidden"):
                if field in case:
                    _string_list(case[field], f"eval_cases[{index}].{field}")


def _check_json_shape(value: Any, field: str, depth: int = 0) -> None:
    if depth > 20:
        raise InputError(f"{field} is nested too deeply")
    if isinstance(value, str):
        _clean_text(value, field, MAX_TEXT)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise InputError(f"{field} must contain only finite numbers")
    elif value is None or isinstance(value, (bool, int)):
        return
    elif isinstance(value, list):
        if len(value) > MAX_ITEMS:
            raise InputError(f"{field} exceeds {MAX_ITEMS} items")
        for index, item in enumerate(value):
            _check_json_shape(item, f"{field}[{index}]", depth + 1)
    elif isinstance(value, dict):
        if len(value) > MAX_ITEMS:
            raise InputError(f"{field} has too many fields")
        for key, item in value.items():
            if not isinstance(key, str) or "\x00" in key or len(key) > 128:
                raise InputError(f"{field} has an invalid field name")
            _check_json_shape(item, f"{field}.{key}", depth + 1)
    else:
        raise InputError(f"{field} contains an unsupported JSON value")


def enforce_protection(previous: dict[str, Any], current: dict[str, Any]) -> None:
    if previous["client_org"] and current["client_org"] != previous["client_org"]:
        raise InputError("client_org cannot be cleared or changed after protection is established")
    if previous["family"] == "client-overlay" and current["family"] != "client-overlay":
        raise InputError("client-overlay family cannot be changed after protection is established")
    if (previous["family"] == "client-overlay" and previous["parent_capability"]
            and current["parent_capability"] != previous["parent_capability"]):
        raise InputError("parent_capability cannot be cleared or changed after protection is established")
    if previous["bfs_firewall"] and not current["bfs_firewall"]:
        raise InputError("bfs_firewall cannot be cleared after protection is established")
    if previous["visibility_lock"] == "permanent-private" and current["visibility_lock"] != "permanent-private":
        raise InputError("visibility_lock cannot be cleared after protection is established")


def validate_graph(graph: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(graph, dict):
        return ["decision must be an object"]
    if set(graph) - {"start", "nodes"}:
        errors.append("decision contains unknown fields")
    start = graph.get("start")
    nodes = graph.get("nodes")
    if not isinstance(start, str) or not start:
        errors.append("decision.start must be a nonempty node ID")
    if not isinstance(nodes, list) or not nodes:
        errors.append("decision.nodes must be a nonempty array")
        return errors
    if len(nodes) > 500:
        errors.append("decision.nodes exceeds 500 nodes")
        return errors
    by_id: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"decision.nodes[{index}] must be an object")
            continue
        unknown = set(node) - {"id", "question", "yes", "no", "result"}
        if unknown:
            errors.append(f"decision node {index} contains unknown fields")
        node_id = node.get("id")
        if not isinstance(node_id, str) or not NODE_RE.fullmatch(node_id):
            errors.append(f"decision.nodes[{index}].id is invalid")
            continue
        if node_id in by_id:
            errors.append(f"decision node ID is duplicated: {node_id}")
        by_id[node_id] = node
        has_question = "question" in node
        has_result = "result" in node
        if has_question == has_result:
            errors.append(f"decision node {node_id} must contain either question or result")
        elif has_question:
            if not isinstance(node.get("question"), str) or not node["question"].strip():
                errors.append(f"decision node {node_id} requires a nonempty question")
            for edge in ("yes", "no"):
                if not isinstance(node.get(edge), str) or not node[edge]:
                    errors.append(f"decision node {node_id} requires a {edge} target")
        elif not isinstance(node.get("result"), str) or not node["result"].strip():
            errors.append(f"decision node {node_id} requires a nonempty result")
    if not isinstance(start, str) or start not in by_id:
        errors.append("decision.start does not reference an existing node")
    for node_id, node in by_id.items():
        if "question" in node:
            for edge in ("yes", "no"):
                target = node.get(edge)
                if isinstance(target, str) and target not in by_id:
                    errors.append(f"decision node {node_id} has dangling {edge} target: {target}")
    if errors:
        return errors

    visiting: set[str] = set()
    visited: set[str] = set()
    reachable: set[str] = set()

    def walk(node_id: str) -> None:
        if node_id in visiting:
            errors.append(f"decision graph contains a cycle at node: {node_id}")
            return
        if node_id in visited:
            reachable.add(node_id)
            return
        visiting.add(node_id)
        reachable.add(node_id)
        node = by_id[node_id]
        if "question" in node:
            walk(node["yes"])
            walk(node["no"])
        visiting.remove(node_id)
        visited.add(node_id)

    walk(start)
    unreachable = sorted(set(by_id) - reachable)
    if unreachable:
        errors.append(f"decision graph has unreachable nodes: {', '.join(unreachable)}")
    return list(dict.fromkeys(errors))


def run_decision(graph: dict[str, Any], answers: dict[str, bool]) -> dict[str, Any]:
    graph_errors = validate_graph(graph)
    if graph_errors:
        raise InputError("; ".join(graph_errors))
    by_id = {node["id"]: node for node in graph["nodes"]}
    current = graph["start"]
    trace: list[str] = []
    while True:
        node = by_id[current]
        trace.append(current)
        if "result" in node:
            return {"complete": True, "result": node["result"], "next": None, "trace": trace}
        if current not in answers:
            return {
                "complete": False,
                "result": None,
                "next": {"id": current, "question": node["question"]},
                "trace": trace,
            }
        current = node["yes"] if answers[current] else node["no"]


def normalize_answers(raw: Any) -> dict[str, bool]:
    if not isinstance(raw, dict) or set(raw) != {"answers"} or not isinstance(raw["answers"], dict):
        raise InputError("body must contain only an answers object")
    answers: dict[str, bool] = {}
    for key, value in raw["answers"].items():
        if not isinstance(key, str) or not NODE_RE.fullmatch(key) or not isinstance(value, bool):
            raise InputError("answers must map valid node IDs to booleans")
        answers[key] = value
    return answers


def validate_answer_nodes(graph: dict[str, Any], answers: dict[str, bool]) -> None:
    question_ids = {
        node.get("id") for node in graph.get("nodes", [])
        if isinstance(node, dict) and "question" in node and isinstance(node.get("id"), str)
    }
    unknown = sorted(set(answers) - question_ids)
    if unknown:
        raise InputError(f"answers reference unknown or non-question nodes: {', '.join(unknown)}")
