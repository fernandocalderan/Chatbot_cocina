from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


_VERTICALS_DIR = Path(__file__).resolve().parent.parent / "verticals"

_ALLOW_LEGACY_FLOW_FILES = os.getenv("ALLOW_LEGACY_FLOW_FILES") == "1"
_FLOW_DIR = Path(__file__).resolve().parent.parent / "flows"
_DEFAULT_VERTICAL_KEY = os.getenv("DEFAULT_VERTICAL_KEY") or "kitchens"

_PLAN_TO_FLOW = {
    "base": "base_plan_fixed",
    "pro": "pro_plan_fixed",
    "elite": "elite_plan_fixed",
}


def list_flow_templates(allowed_ids: set[str] | None = None) -> list[dict[str, str]]:
    # Deprecado: los flows ya no se exponen desde `app/flows` (solo migración controlada).
    if not _ALLOW_LEGACY_FLOW_FILES:
        return []
    items = []
    for path in sorted(_FLOW_DIR.glob("*.json")):
        flow_id = path.stem
        if allowed_ids and flow_id not in allowed_ids:
            continue
        label = flow_id.replace("_", " ").title()
        items.append({"id": flow_id, "label": label})
    return items


def load_flow_template(
    flow_id: str | None,
    plan_value: str | None = None,
    *,
    vertical_key: str | None = None,
    scopes: list[str] | None = None,
) -> dict[str, Any]:
    # Source-of-truth for vertical tenants: `app/verticals/<vertical_key>/flow_base.json`
    chosen_vertical = (str(vertical_key).strip() if vertical_key else "") or _DEFAULT_VERTICAL_KEY
    v_dir = _VERTICALS_DIR / chosen_vertical
    v_path = v_dir / "flow_base.json"
    if v_path.exists():
        base: dict[str, Any] = {}
        try:
            with v_path.open(encoding="utf-8") as f:
                base_raw = json.load(f)
            base = base_raw if isinstance(base_raw, dict) else {}
        except Exception:
            base = {}

        def _normalize_scopes(raw: object) -> list[str]:
            if not raw:
                return []
            if isinstance(raw, list):
                items = [str(s).strip() for s in raw if s]
            elif isinstance(raw, tuple):
                items = [str(s).strip() for s in raw if s]
            elif isinstance(raw, str):
                items = [raw.strip()]
            else:
                return []
            out: list[str] = []
            seen: set[str] = set()
            for s in items:
                if not s or s in seen:
                    continue
                seen.add(s)
                out.append(s)
            return out

        def _deep_merge(base_obj: Any, override_obj: Any) -> Any:
            if not isinstance(base_obj, dict) or not isinstance(override_obj, dict):
                return override_obj
            merged = dict(base_obj)
            for k, v in override_obj.items():
                if isinstance(v, dict) and isinstance(merged.get(k), dict):
                    merged[k] = _deep_merge(merged.get(k), v)
                else:
                    merged[k] = v
            return merged

        chosen_scopes = _normalize_scopes(scopes)
        if len(chosen_scopes) == 1:
            scope_key = chosen_scopes[0]
            scope_path = v_dir / f"flow_scope_{scope_key}.json"
            if scope_path.exists():
                try:
                    with scope_path.open(encoding="utf-8") as f:
                        data = json.load(f)
                    return data if isinstance(data, dict) else base
                except Exception:
                    return base

            meta_path = v_dir / "metadata.json"
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            except Exception:
                meta = {}
            defs = meta.get("scope_definitions") if isinstance(meta, dict) else None
            entry = defs.get(scope_key) if isinstance(defs, dict) else None
            overrides = entry.get("flow_overrides") if isinstance(entry, dict) else None
            if isinstance(overrides, dict) and overrides:
                merged = _deep_merge(base, overrides)
                return merged if isinstance(merged, dict) else base

        return base

    if not _ALLOW_LEGACY_FLOW_FILES:
        return {}

    if flow_id:
        path = _FLOW_DIR / f"{flow_id}.json"
        if path.exists():
            with path.open(encoding="utf-8") as f:
                return json.load(f)
    plan_norm = (plan_value or "base").lower()
    fallback_id = _PLAN_TO_FLOW.get(plan_norm, "base_plan_fixed")
    path = _FLOW_DIR / f"{fallback_id}.json"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    return {}


def _merge_text(original: Any, override: Any) -> Any:
    if override is None:
        return original
    if isinstance(original, dict) and isinstance(override, dict):
        merged = dict(original)
        merged.update({k: v for k, v in override.items() if v is not None})
        return merged
    return override


def apply_materials(flow_data: dict, materials: dict | None) -> dict:
    if not materials or not isinstance(flow_data, dict):
        return flow_data
    content = materials.get("content") if isinstance(materials.get("content"), dict) else {}
    questions = content.get("questions") if isinstance(content.get("questions"), dict) else {}
    buttons = content.get("buttons") if isinstance(content.get("buttons"), dict) else {}
    welcome = content.get("welcome")
    closing = content.get("closing")

    blocks = flow_data.get("blocks") if isinstance(flow_data.get("blocks"), dict) else {}
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        if block_id in questions:
            block["text"] = _merge_text(block.get("text"), questions.get(block_id))
        if block_id in buttons and block.get("type") in {"buttons", "options"}:
            override = buttons.get(block_id)
            opts = block.get("options") if isinstance(block.get("options"), list) else []
            if isinstance(override, list):
                for idx, opt in enumerate(opts):
                    if idx >= len(override):
                        break
                    if isinstance(opt, dict):
                        opt["label"] = _merge_text(opt.get("label"), override[idx])
            elif isinstance(override, dict):
                for opt in opts:
                    if not isinstance(opt, dict):
                        continue
                    opt_id = opt.get("value") or opt.get("id") or opt.get("label")
                    if opt_id in override:
                        opt["label"] = _merge_text(opt.get("label"), override.get(opt_id))

    if welcome:
        start_id = flow_data.get("start_block") or "welcome"
        if start_id in blocks and isinstance(blocks[start_id], dict):
            blocks[start_id]["text"] = _merge_text(blocks[start_id].get("text"), welcome)
    if closing:
        if "end" in blocks and isinstance(blocks["end"], dict):
            blocks["end"]["text"] = _merge_text(blocks["end"].get("text"), closing)
    return flow_data
