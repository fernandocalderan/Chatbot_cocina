from __future__ import annotations

import json
from pathlib import Path

from app.services.flow_resolver import resolve_flow_for_scope


BASE_DIR = Path(__file__).resolve().parents[2]
VERT_DIR = BASE_DIR / "backend" / "app" / "verticals"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _scopes_from_metadata(meta: dict) -> list[str]:
    scopes = meta.get("scopes")
    if isinstance(scopes, dict) and scopes:
        return list(scopes.keys())
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    scope_cfg = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
    included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else list(scope_defs.keys())
    return [str(s) for s in included if s]


def test_flow_resolver_smoke_all_scopes():
    registry = _read_json(VERT_DIR / "registry.json")
    for vkey in registry.keys():
        meta_path = VERT_DIR / vkey / "metadata.json"
        meta = _read_json(meta_path)
        scopes = _scopes_from_metadata(meta)
        for scope_key in scopes:
            flow, source = resolve_flow_for_scope(vkey, scope_key)
            assert isinstance(flow, dict)
            assert source is None or source.endswith(".json") or source == "metadata.flow_overrides"
