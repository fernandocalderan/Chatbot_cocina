#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from __future__ import annotations

from pathlib import Path
import json
import re
import sys

ROOT = Path.cwd()
VERT_DIR = ROOT / "backend" / "app" / "verticals"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        err(f"{path}: JSON inválido ({exc})")
        return {}


def validate_flow(flow: dict, *, path: Path) -> None:
    if not isinstance(flow, dict):
        err(f"{path}: flow no es dict")
        return
    blocks = flow.get("blocks")
    if not isinstance(blocks, dict) or not blocks:
        err(f"{path}: flow.blocks ausente")
        return
    ids = set(blocks.keys())
    start = flow.get("start_block")
    if not isinstance(start, str) or start not in ids:
        err(f"{path}: start_block inválido ({start})")

    def check_ref(ref: object, ctx: str) -> None:
        if ref is None:
            return
        if not isinstance(ref, str) or not ref.strip():
            return
        if ref not in ids:
            err(f"{path}: referencia inválida {ctx} -> {ref}")

    for bid, block in blocks.items():
        if not isinstance(block, dict):
            warn(f"{path}: bloque no dict ({bid})")
            continue
        check_ref(block.get("next"), f"{bid}.next")
        nm = block.get("next_map")
        if isinstance(nm, dict):
            for k, v in nm.items():
                check_ref(v, f"{bid}.next_map[{k}]")
        branches = block.get("branches")
        if isinstance(branches, dict):
            for k, v in branches.items():
                check_ref(v, f"{bid}.branches[{k}]")
        if block.get("type") == "condition":
            conditions = block.get("conditions")
            if isinstance(conditions, list):
                for idx, cond in enumerate(conditions):
                    if isinstance(cond, dict):
                        check_ref(cond.get("next"), f"{bid}.conditions[{idx}].next")


def parse_subflow_filename(name: str) -> tuple[str, str, str] | None:
    if not name.startswith("subflow_scope_") or not name.endswith(".json"):
        return None
    rest = name.removeprefix("subflow_scope_").removesuffix(".json")
    parts = rest.split("__")
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


if not VERT_DIR.exists():
    print("No se encontró backend/app/verticals")
    sys.exit(1)

for vdir in sorted(VERT_DIR.iterdir()):
    if not vdir.is_dir():
        continue
    vkey = vdir.name
    meta_path = vdir / "metadata.json"
    if not meta_path.exists():
        warn(f"{vdir}: metadata.json faltante")
        continue
    meta = load_json(meta_path)
    if str(meta.get("vertical_key") or vkey) != vkey:
        warn(f"{meta_path}: vertical_key no coincide con carpeta ({vkey})")
    default_flow_id = meta.get("default_flow_id")
    flow_ids = meta.get("flow_ids") if isinstance(meta.get("flow_ids"), list) else []
    if default_flow_id and default_flow_id not in flow_ids:
        warn(f"{meta_path}: default_flow_id no está en flow_ids")

    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    scope_cfg = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
    included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else []
    for sk in included:
        if sk not in scope_defs:
            warn(f"{meta_path}: scope incluido sin definición: {sk}")
    for sk, sdef in scope_defs.items():
        if not isinstance(sdef, dict):
            warn(f"{meta_path}: scope_definitions[{sk}] no dict")
            continue
        if "flow_id" not in sdef:
            warn(f"{meta_path}: scope[{sk}] sin flow_id")
        if "problem_groups" not in sdef:
            warn(f"{meta_path}: scope[{sk}] sin problem_groups")

    flow_base = vdir / "flow_base.json"
    if not flow_base.exists():
        warn(f"{flow_base}: faltante")
    else:
        validate_flow(load_json(flow_base), path=flow_base)

    for flow_path in vdir.glob("flow_base_scope_*.json"):
        validate_flow(load_json(flow_path), path=flow_path)

    for sf_path in vdir.glob("subflow_scope_*__*__*.json"):
        parsed = parse_subflow_filename(sf_path.name)
        if not parsed:
            warn(f"{sf_path}: nombre inválido")
            continue
        scope, save_to, key = parsed
        data = load_json(sf_path)
        validate_flow(data, path=sf_path)
        cfg = data.get("config") if isinstance(data.get("config"), dict) else {}
        sub = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
        for field in ("vertical_key", "scope", "router_save_to", "key"):
            if not str(sub.get(field) or "").strip():
                err(f"{sf_path}: config.subflow.{field} faltante")
        if str(sub.get("scope") or scope) != scope:
            warn(f"{sf_path}: config.subflow.scope no coincide")
        if str(sub.get("router_save_to") or save_to) != save_to:
            warn(f"{sf_path}: config.subflow.router_save_to no coincide")
        if str(sub.get("key") or key) != key:
            warn(f"{sf_path}: config.subflow.key no coincide")

        problem = cfg.get("problem") if isinstance(cfg.get("problem"), dict) else {}
        for field in ("group", "title", "symptoms", "key_questions", "base_answer", "fields_to_capture"):
            if field not in problem:
                warn(f"{sf_path}: problem.{field} faltante")
        if problem.get("symptoms") is not None and not isinstance(problem.get("symptoms"), list):
            err(f"{sf_path}: problem.symptoms debe ser lista")
        if problem.get("key_questions") is not None and not isinstance(problem.get("key_questions"), list):
            err(f"{sf_path}: problem.key_questions debe ser lista")
        if problem.get("fields_to_capture") is not None and not isinstance(problem.get("fields_to_capture"), list):
            err(f"{sf_path}: problem.fields_to_capture debe ser lista")

print("QA Verticals:")
if errors:
    print("Errores:")
    for msg in errors:
        print(f"- {msg}")
if warnings:
    print("Advertencias:")
    for msg in warnings:
        print(f"- {msg}")
if errors:
    sys.exit(1)
print("OK")
PY
