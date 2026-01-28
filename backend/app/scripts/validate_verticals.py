from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
VERT_DIR = BASE_DIR / "app" / "verticals"
REGISTRY_PATH = VERT_DIR / "registry.json"

RE_VERTICAL = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
RE_SCOPE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")
RE_GROUP = re.compile(r"^[a-z0-9][a-z0-9_-]{0,30}$")
RE_PROBLEM = re.compile(r"^[a-z0-9][a-z0-9_-]{0,40}$")


class Collector:
    def __init__(self, strict: bool) -> None:
        self.strict = strict
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.orphans: list[str] = []
        self.fixes: dict[str, dict[str, Any]] = {}

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def orphan(self, msg: str) -> None:
        self.orphans.append(msg)

    def add_fix(self, vkey: str, field: str, value: Any) -> None:
        self.fixes.setdefault(vkey, {})
        self.fixes[vkey][field] = value

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


def slug_ok(rex: re.Pattern[str], value: str) -> bool:
    return bool(rex.match(value))


def parse_legacy_subflow_filename(name: str) -> tuple[str, str, str] | None:
    if not name.startswith("subflow_scope_") or not name.endswith(".json"):
        return None
    rest = name.removeprefix("subflow_scope_").removesuffix(".json")
    parts = rest.split("__")
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def collect_subflows(vdir: Path, col: Collector) -> tuple[dict[str, dict[str, set[str]]], bool]:
    """
    Returns problems_by_scope_group[scope][group] = {problem_key}
    and whether canonical layout is used.
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
                    by_scope.setdefault(scope, {}).setdefault(group, set()).add(p.stem)
    else:
        for sf in vdir.glob("subflow_scope_*__*__*.json"):
            parsed = parse_legacy_subflow_filename(sf.name)
            if not parsed:
                col.warn(f"{sf}: nombre inválido")
                continue
            scope, group, problem = parsed
            by_scope.setdefault(scope, {}).setdefault(group, set()).add(problem)
    return by_scope, used_canonical


def validate_playbook_v2(flow: dict[str, Any], *, vkey: str, scope_key: str, col: Collector) -> None:
    identity = flow.get("identity") if isinstance(flow.get("identity"), dict) else {}
    objectives = flow.get("objectives") if isinstance(flow.get("objectives"), list) else []
    steps = flow.get("steps") if isinstance(flow.get("steps"), list) else []

    def _mark(level: str, msg: str) -> None:
        if level == "error":
            col.err(msg)
        else:
            col.warn(msg)

    if not identity:
        _mark("warning", f"{vkey}/{scope_key}: playbook V2 sin identity")
        return

    role = str(identity.get("role") or "").strip()
    tone = str(identity.get("tone") or "").strip()
    if not role or not tone:
        _mark("warning", f"{vkey}/{scope_key}: identity.role/tone incompletos")

    if len([o for o in objectives if str(o).strip()]) < 2:
        _mark("warning", f"{vkey}/{scope_key}: objectives insuficientes")

    if len(steps) < 5:
        _mark("warning", f"{vkey}/{scope_key}: steps insuficientes (<5)")

    # Cobertura mínima de categorías (si hay campos).
    categories = set()
    for st in steps:
        if not isinstance(st, dict):
            continue
        cat = st.get("category") or st.get("type") or st.get("id")
        if isinstance(cat, str):
            categories.add(cat.lower())
        tags = st.get("tags")
        if isinstance(tags, list):
            categories.update([str(t).lower() for t in tags if t])
    required = {"urgency", "context", "diagnosis", "proposal", "cta"}
    if categories:
        missing = [c for c in required if all(c not in x for x in categories)]
        if missing:
            _mark("warning", f"{vkey}/{scope_key}: faltan categorías {', '.join(missing)}")

    if col.strict:
        # En modo strict, elevar warnings de playbook V2 a errores.
        last_warns = [w for w in col.warnings if f"{vkey}/{scope_key}" in w]
        for msg in last_warns:
            if msg in col.warnings:
                col.warnings.remove(msg)
            col.err(msg.replace("warning", "error"))


def resolve_scopes(meta: dict[str, Any], col: Collector) -> dict[str, dict[str, Any]]:
    scopes = meta.get("scopes")
    if isinstance(scopes, dict) and scopes:
        return scopes
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    scope_cfg = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
    included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else list(scope_defs.keys())
    if not included:
        col.warn("metadata sin scopes definidos")
        return {}
    legacy = {}
    for sk in included:
        entry = scope_defs.get(sk) if isinstance(scope_defs.get(sk), dict) else {}
        legacy[sk] = {"label": entry.get("label") or sk}
    col.warn("metadata.scopes ausente (legacy scope_definitions)")
    return legacy


def validate_vertical(vkey: str, entry: dict[str, Any], col: Collector, *, fix_dry_run: bool) -> None:
    if not slug_ok(RE_VERTICAL, vkey):
        col.err(f"registry.json: vertical_key inválido: {vkey}")
        return
    if "path" not in entry:
        col.warn(f"{vkey}: registry sin path")
    if "archived" not in entry:
        col.warn(f"{vkey}: registry sin archived")

    vdir = VERT_DIR / str(entry.get("path") or vkey)
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

    scopes = resolve_scopes(meta, col)
    default_scope = meta.get("default_scope")
    if not default_scope and scopes:
        col.warn(f"{vkey}: default_scope faltante")
        if fix_dry_run:
            col.add_fix(vkey, "default_scope", next(iter(scopes.keys())))

    problems_by_scope, used_canonical = collect_subflows(vdir, col)
    if not used_canonical:
        col.warn(f"{vkey}: layout legacy de subflows (subflow_scope_*)")

    # Build groups for dry-run fix (from subflows on disk).
    if fix_dry_run and "scopes" not in meta:
        dry_scopes = {}
        for sk, sdef in scopes.items():
            dry_scopes[sk] = {
                "label": sdef.get("label") or sk,
                "flow_id": f"flow_base_scope_{sk}.json" if (vdir / f"flow_base_scope_{sk}.json").exists() else "flow_base.json",
                "problem_groups": sorted(problems_by_scope.get(sk, {}).keys()),
                "archived": False,
            }
        col.add_fix(vkey, "scopes", dry_scopes)

    referenced_groups: set[tuple[str, str]] = set()
    for scope_key, sdef in scopes.items():
        if not slug_ok(RE_SCOPE, scope_key):
            col.err(f"{vkey}: scope_key inválido: {scope_key}")
        if not isinstance(sdef, dict):
            col.err(f"{vkey}: scope {scope_key} no es dict")
            continue

        flow_id = str(sdef.get("flow_id") or "").strip()
        scope_flow = vdir / f"flow_base_scope_{scope_key}.json"
        legacy_flow = vdir / f"flow_scope_{scope_key}.json"
        base_flow = vdir / "flow_base.json"
        if flow_id.endswith(".json"):
            if not (vdir / flow_id).exists():
                col.err(f"{vkey}: scope {scope_key} flow file faltante: {flow_id}")
        else:
            if not (scope_flow.exists() or legacy_flow.exists() or base_flow.exists()):
                col.err(f"{vkey}: scope {scope_key} sin flow en disco")

        # Validate V2 playbook if present
        flow_path = scope_flow if scope_flow.exists() else (legacy_flow if legacy_flow.exists() else base_flow)
        if flow_path.exists():
            flow = load_json(flow_path, col)
            if isinstance(flow, dict) and ("steps" in flow or "identity" in flow):
                validate_playbook_v2(flow, vkey=vkey, scope_key=scope_key, col=col)
            else:
                col.warn(f"{vkey}/{scope_key}: flow legacy (blocks) sin playbook V2")

        groups = sdef.get("problem_groups")
        if groups is None:
            col.warn(f"{vkey}: scope {scope_key} sin problem_groups")
            groups = []
        if not isinstance(groups, list):
            col.err(f"{vkey}: scope {scope_key} problem_groups no es lista")
            groups = []
        for g in groups:
            gkey = str(g)
            if not slug_ok(RE_GROUP, gkey):
                col.err(f"{vkey}: group_key inválido ({scope_key}): {gkey}")
            referenced_groups.add((scope_key, gkey))

    # Orphans: problems on disk not referenced by metadata groups
    for scope_key, groups in problems_by_scope.items():
        for group_key, problems in groups.items():
            if (scope_key, group_key) not in referenced_groups:
                col.orphan(f"{vkey}: orphan group {scope_key}/{group_key} ({len(problems)} problems)")
            for pkey in problems:
                if not slug_ok(RE_PROBLEM, pkey):
                    col.err(f"{vkey}: problem_key inválido {scope_key}/{group_key}/{pkey}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate verticals contract + references")
    parser.add_argument("--strict", action="store_true", help="Fail on orphans")
    parser.add_argument("--vertical", action="append", help="Filter by vertical_key (repeatable)")
    parser.add_argument("--fix-dry-run", action="store_true", help="Print suggested fixes without writing")
    args = parser.parse_args()

    col = Collector(strict=args.strict)
    if not REGISTRY_PATH.exists():
        col.err("registry.json faltante")
    else:
        registry = load_json(REGISTRY_PATH, col)
        if not isinstance(registry, dict):
            col.err("registry.json inválido")
        else:
            requested = [v.strip() for v in (args.vertical or []) if v.strip()]
            keys = requested or list(registry.keys())
            for vkey in keys:
                entry = registry.get(vkey)
                if not isinstance(entry, dict):
                    col.err(f"registry.json: entry inválido para {vkey}")
                    continue
                validate_vertical(vkey, entry, col, fix_dry_run=bool(args.fix_dry_run))

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
    if args.fix_dry_run and col.fixes:
        print("Fix dry-run (sugerencias):")
        print(json.dumps(col.fixes, ensure_ascii=False, indent=2))

    if col.ok():
        print("OK")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
