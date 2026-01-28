from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VERT_DIR = ROOT / "app" / "verticals"
REGISTRY = VERT_DIR / "registry.json"

VERTICAL_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
SCOPE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
GROUP_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,30}$")
PROBLEM_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,40}$")


class Collector:
    def __init__(self, strict: bool) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.orphans: list[str] = []
        self.strict = strict

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def orphan(self, msg: str) -> None:
        self.orphans.append(msg)

    def ok(self) -> bool:
        if self.errors:
            return False
        if self.strict and self.orphans:
            return False
        return True


def load_json(path: Path, col: Collector) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        col.err(f"{path}: JSON inválido ({exc})")
        return {}


def parse_legacy_subflow_filename(name: str) -> tuple[str, str, str] | None:
    if not name.startswith("subflow_scope_") or not name.endswith(".json"):
        return None
    rest = name.removeprefix("subflow_scope_").removesuffix(".json")
    parts = rest.split("__")
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def slug_ok(rex: re.Pattern[str], value: str) -> bool:
    return bool(rex.match(value))


def collect_subflows(vdir: Path, col: Collector) -> tuple[dict[str, dict[str, set[str]]], bool]:
    """
    Returns problems_by_scope_group[scope][group] = {problem_key}
    and whether canonical subflows/ layout exists.
    """
    by_scope: dict[str, dict[str, set[str]]] = {}
    canonical_root = vdir / "subflows"
    used_canonical = False

    if canonical_root.exists():
        used_canonical = True
        for scope_dir in canonical_root.iterdir():
            if not scope_dir.is_dir():
                continue
            scope = scope_dir.name
            for group_dir in scope_dir.iterdir():
                if not group_dir.is_dir():
                    continue
                group = group_dir.name
                for p in group_dir.glob("*.json"):
                    problem = p.stem
                    by_scope.setdefault(scope, {}).setdefault(group, set()).add(problem)
    else:
        for sf in vdir.glob("subflow_scope_*__*__*.json"):
            parsed = parse_legacy_subflow_filename(sf.name)
            if not parsed:
                col.warn(f"{sf}: nombre inválido")
                continue
            scope, group, problem = parsed
            by_scope.setdefault(scope, {}).setdefault(group, set()).add(problem)

    return by_scope, used_canonical


def validate_scope_flow(vdir: Path, scope_key: str, flow_id: str | None, col: Collector) -> None:
    if not flow_id:
        col.err(f"{vdir.name}: scope {scope_key} sin flow_id")
        return
    if flow_id.endswith(".json"):
        path = vdir / flow_id
        if not path.exists():
            col.err(f"{vdir.name}: scope {scope_key} flow file faltante: {flow_id}")
        return
    # non-file flow id: fallback to scope file or base flow
    scope_path = vdir / f"flow_base_scope_{scope_key}.json"
    legacy_path = vdir / f"flow_scope_{scope_key}.json"
    base = vdir / "flow_base.json"
    if scope_path.exists() or legacy_path.exists() or base.exists():
        return
    col.err(f"{vdir.name}: scope {scope_key} sin flow en disco")


def validate_vertical(vkey: str, entry: dict[str, Any], col: Collector) -> None:
    if not slug_ok(VERTICAL_RE, vkey):
        col.err(f"registry.json: vertical_key inválido: {vkey}")
        return
    path_key = str(entry.get("path") or vkey).strip() or vkey
    vdir = VERT_DIR / path_key
    if not vdir.exists():
        col.err(f"{vkey}: carpeta faltante ({vdir})")
        return
    meta_path = vdir / "metadata.json"
    if not meta_path.exists():
        col.err(f"{vkey}: metadata.json faltante")
        return
    meta = load_json(meta_path, col)
    if str(meta.get("vertical_key") or vkey) != vkey:
        col.warn(f"{vkey}: metadata.vertical_key no coincide")

    default_scope = meta.get("default_scope")
    scopes_contract = meta.get("scopes") if isinstance(meta.get("scopes"), dict) else None
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    if scopes_contract:
        scopes = scopes_contract
    else:
        scopes = {k: {"label": v.get("label") if isinstance(v, dict) else k} for k, v in scope_defs.items()}
        col.warn(f"{vkey}: metadata.scopes no definido (usando scope_definitions)")

    if default_scope and default_scope not in scopes:
        col.warn(f"{vkey}: default_scope no existe en scopes")

    # Validate subflows
    problems_by_scope, used_canonical = collect_subflows(vdir, col)
    if not used_canonical:
        col.warn(f"{vkey}: layout legacy de subflows (subflow_scope_*)")
    else:
        # ensure subflows/<scope> exists for each scope
        for sk in scopes.keys():
            scope_dir = vdir / "subflows" / sk
            if not scope_dir.exists():
                col.warn(f"{vkey}: carpeta subflows/{sk} faltante")

    for scope_key, sdef in scopes.items():
        if not slug_ok(SCOPE_RE, scope_key):
            col.err(f"{vkey}: scope_key inválido: {scope_key}")
        if not isinstance(sdef, dict):
            col.err(f"{vkey}: scope {scope_key} no es dict")
            continue
        flow_id = sdef.get("flow_id")
        validate_scope_flow(vdir, scope_key, str(flow_id) if flow_id else None, col)
        groups = sdef.get("problem_groups")
        if groups is None:
            col.warn(f"{vkey}: scope {scope_key} sin problem_groups")
            groups = []
        if not isinstance(groups, list):
            col.err(f"{vkey}: scope {scope_key} problem_groups no es lista")
            groups = []
        for g in groups:
            gkey = str(g)
            if not slug_ok(GROUP_RE, gkey):
                col.err(f"{vkey}: group_key inválido ({scope_key}): {gkey}")
            probs = problems_by_scope.get(scope_key, {}).get(gkey, set())
            if not probs:
                col.warn(f"{vkey}: scope {scope_key} group {gkey} sin problemas")

    # Orphans: problems on disk not referenced by metadata groups
    referenced: set[tuple[str, str]] = set()
    for scope_key, sdef in scopes.items():
        if not isinstance(sdef, dict):
            continue
        groups = sdef.get("problem_groups")
        if isinstance(groups, list):
            for g in groups:
                referenced.add((scope_key, str(g)))

    for scope_key, groups in problems_by_scope.items():
        for group_key, problems in groups.items():
            if (scope_key, group_key) not in referenced:
                col.orphan(f"{vkey}: orphan group {scope_key}/{group_key} ({len(problems)} problems)")
            for pkey in problems:
                if not slug_ok(PROBLEM_RE, pkey):
                    col.err(f"{vkey}: problem_key inválido {scope_key}/{group_key}/{pkey}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate verticals contract + references")
    parser.add_argument("--strict", action="store_true", help="Fail on orphans and warnings")
    args = parser.parse_args()

    col = Collector(strict=args.strict)
    if not REGISTRY.exists():
        col.err("registry.json faltante")
    else:
        registry = load_json(REGISTRY, col)
        for vkey, entry in registry.items():
            if not isinstance(entry, dict):
                col.err(f"registry.json: entry inválido para {vkey}")
                continue
            validate_vertical(str(vkey), entry, col)

    if col.errors:
        print("Errores:")
        for msg in col.errors:
            print(f"- {msg}")
    if col.warnings:
        print("Advertencias:")
        for msg in col.warnings:
            print(f"- {msg}")
    if col.orphans:
        print("Orphans:")
        for msg in col.orphans:
            print(f"- {msg}")
    if col.ok():
        print("OK")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
