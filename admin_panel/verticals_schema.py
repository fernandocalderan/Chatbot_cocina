from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
SUBFLOW_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,30}$")


@dataclass
class ValidationIssue:
    level: str  # "error" or "warning"
    message: str


@dataclass(frozen=True)
class ProblemSchema:
    group: str
    title: str
    symptoms: list[str]
    key_questions: list[str]
    base_answer: str
    fields_to_capture: list[str]
    cta: str


@dataclass(frozen=True)
class FlowSchema:
    identity: str
    goals: list[str]
    steps: list[str]
    rules_toggles: list[str]


@dataclass(frozen=True)
class ScopeSchema:
    scope_key: str
    label: str
    flow_id: str | None
    problem_groups: list[str]


@dataclass(frozen=True)
class VerticalSchema:
    key: str
    label: str
    scopes: list[ScopeSchema]
    default_flow_id: str | None
    flow_ids: list[str]
    assets: dict[str, Any]
    locks: dict[str, Any]
    archived: bool


def _as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_problem(problem: dict | None, *, default_group: str, title: str) -> dict[str, Any]:
    problem = problem if isinstance(problem, dict) else {}
    symptoms = [str(s).strip() for s in _as_list(problem.get("symptoms")) if str(s).strip()]
    key_questions = problem.get("key_questions")
    if key_questions is None:
        key_questions = problem.get("questions")
    key_questions = [str(s).strip() for s in _as_list(key_questions) if str(s).strip()]
    base_answer = problem.get("base_answer")
    if base_answer is None:
        base_answer = problem.get("response")
    base_answer = str(base_answer or "").strip()
    fields_to_capture = [str(s).strip() for s in _as_list(problem.get("fields_to_capture")) if str(s).strip()]
    cta = str(problem.get("cta") or "").strip()
    group = str(problem.get("group") or default_group or "").strip()
    title_val = str(problem.get("title") or title or "").strip()
    return {
        "group": group,
        "title": title_val,
        "symptoms": symptoms,
        "key_questions": key_questions,
        "base_answer": base_answer,
        "cta": cta,
        "fields_to_capture": fields_to_capture,
    }


def unique_slug(base: str, existing: set[str]) -> str:
    base = str(base or "").strip().lower().replace(" ", "_")
    if not base:
        base = "item"
    if base not in existing:
        return base
    idx = 2
    while True:
        candidate = f"{base}_{idx}"
        if candidate not in existing:
            return candidate
        idx += 1


def validate_problem(problem: dict | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    problem = problem if isinstance(problem, dict) else {}
    group = str(problem.get("group") or "").strip()
    if group and not SUBFLOW_KEY_RE.match(group):
        issues.append(ValidationIssue("warning", f"problem.group inválido: {group}"))
    title = str(problem.get("title") or "").strip()
    if not title:
        issues.append(ValidationIssue("warning", "problem.title vacío"))
    symptoms = problem.get("symptoms")
    if symptoms is not None and not isinstance(symptoms, list):
        issues.append(ValidationIssue("error", "problem.symptoms debe ser lista"))
    questions = problem.get("key_questions")
    if questions is not None and not isinstance(questions, list):
        issues.append(ValidationIssue("error", "problem.key_questions debe ser lista"))
    fields = problem.get("fields_to_capture")
    if fields is not None and not isinstance(fields, list):
        issues.append(ValidationIssue("error", "problem.fields_to_capture debe ser lista"))
    return issues


def validate_metadata(meta: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(meta, dict):
        return [ValidationIssue("error", "metadata no es dict")]
    vkey = str(meta.get("vertical_key") or "").strip().lower()
    if not vkey or not KEY_RE.match(vkey):
        issues.append(ValidationIssue("error", "metadata.vertical_key inválido"))
    label = str(meta.get("label") or "").strip()
    if not label:
        issues.append(ValidationIssue("warning", "metadata.label vacío"))
    default_flow_id = str(meta.get("default_flow_id") or "").strip()
    flow_ids = meta.get("flow_ids") if isinstance(meta.get("flow_ids"), list) else []
    if default_flow_id and default_flow_id not in flow_ids:
        issues.append(ValidationIssue("warning", "default_flow_id no está en flow_ids"))
    if flow_ids:
        if len(set(flow_ids)) != len(flow_ids):
            issues.append(ValidationIssue("error", "flow_ids contiene duplicados"))
    archived = meta.get("archived")
    if archived is not None and not isinstance(archived, bool):
        issues.append(ValidationIssue("warning", "metadata.archived debe ser booleano"))
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    scope_cfg = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
    included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else []
    seen = set()
    for k in scope_defs.keys():
        if not KEY_RE.match(str(k)):
            issues.append(ValidationIssue("warning", f"scope_key inválido: {k}"))
        if k in seen:
            issues.append(ValidationIssue("error", f"scope duplicado: {k}"))
        seen.add(k)
    for k in included:
        if k not in scope_defs:
            issues.append(ValidationIssue("warning", f"scope incluido sin definición: {k}"))
    flow_ids_seen: set[str] = set()
    for sk, sdef in scope_defs.items():
        if not isinstance(sdef, dict):
            issues.append(ValidationIssue("warning", f"scope_definitions[{sk}] no es dict"))
            continue
        flow_id = sdef.get("flow_id")
        if flow_id:
            flow_id = str(flow_id).strip()
            if flow_id in flow_ids_seen:
                issues.append(ValidationIssue("warning", f"flow_id duplicado entre scopes: {flow_id}"))
            flow_ids_seen.add(flow_id)
        groups = sdef.get("problem_groups")
        if groups is not None and not isinstance(groups, list):
            issues.append(ValidationIssue("warning", f"scope[{sk}].problem_groups debe ser lista"))
    return issues


def validate_flow(flow: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(flow, dict):
        return [ValidationIssue("error", "flow no es dict")]
    blocks = flow.get("blocks")
    if not isinstance(blocks, dict) or not blocks:
        return [ValidationIssue("error", "flow.blocks ausente")]
    ids = set(str(k) for k in blocks.keys() if k)
    start = flow.get("start_block")
    if not isinstance(start, str) or start not in ids:
        issues.append(ValidationIssue("error", "start_block inválido"))

    def _check_next(next_id: Any, ctx: str):
        if next_id is None:
            return
        if not isinstance(next_id, str) or not next_id.strip():
            return
        if next_id not in ids:
            issues.append(ValidationIssue("error", f"Referencia inválida {ctx}: {next_id}"))

    for bid, block in blocks.items():
        if not isinstance(block, dict):
            issues.append(ValidationIssue("warning", f"block no es dict: {bid}"))
            continue
        _check_next(block.get("next"), f"{bid}.next")
        nm = block.get("next_map")
        if isinstance(nm, dict):
            for k, v in nm.items():
                _check_next(v, f"{bid}.next_map[{k}]")
    return issues


def validate_subflow_config(cfg: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sub = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
    if not sub:
        issues.append(ValidationIssue("error", "config.subflow faltante"))
        return issues
    for key in ("vertical_key", "scope", "router_save_to", "key"):
        if not str(sub.get(key) or "").strip():
            issues.append(ValidationIssue("error", f"config.subflow.{key} faltante"))
    return issues
