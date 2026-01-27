from __future__ import annotations

import copy
from typing import Any

from sqlalchemy.orm import Session

from app.models.tenants import Tenant
from app.services.subflow_overrides import (
    apply_overrides_to_flow,
    get_composition_mode,
    get_enabled_map,
    get_order_list,
    load_overrides_payload,
)
from app.services.verticals import (
    get_vertical_config,
    tenant_vertical_scopes,
    vertical_list_subflows,
    vertical_read_asset_json,
)


def _subflow_enabled(payload: dict) -> bool:
    cfg = payload.get("config") if isinstance(payload.get("config"), dict) else {}
    meta = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
    if meta.get("disabled") is True:
        return False
    if meta.get("enabled") is False:
        return False
    return True


def _resolve_scope_for_tenant(tenant: Tenant | None) -> str | None:
    scopes = tenant_vertical_scopes(tenant) if tenant else []
    if scopes:
        return str(scopes[0]).strip().lower() or None
    return "default"


def _subflow_config(vertical_key: str | None) -> dict[str, Any]:
    cfg = get_vertical_config(vertical_key)
    sub = cfg.get("subflows") if isinstance(cfg, dict) else None
    return sub if isinstance(sub, dict) else {}


def _subflow_locks(vertical_key: str | None) -> dict[str, Any]:
    sub = _subflow_config(vertical_key)
    locks = sub.get("locks") if isinstance(sub.get("locks"), dict) else {}
    return locks if isinstance(locks, dict) else {}


def _recommended_order(vertical_key: str | None) -> list[str]:
    sub = _subflow_config(vertical_key)
    order = sub.get("recommended_order")
    if isinstance(order, list):
        return [str(x) for x in order if x]
    return []


def _composition_default(vertical_key: str | None) -> str:
    sub = _subflow_config(vertical_key)
    return str(sub.get("composition_default") or "router").strip().lower()


def _is_required(locks: dict[str, Any], key: str) -> bool:
    entry = locks.get(key) if isinstance(locks, dict) else None
    return bool(entry.get("required")) if isinstance(entry, dict) else False


def _is_editable(locks: dict[str, Any], key: str) -> bool:
    entry = locks.get(key) if isinstance(locks, dict) else None
    if not isinstance(entry, dict):
        return True
    if entry.get("editable") is False:
        return False
    if entry.get("locked") is True:
        return False
    return True


def _coalesce_order(order: list[str], recommended: list[str], keys: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    def _add(items: list[str]):
        for raw in items:
            k = str(raw or "").strip()
            if not k or k in seen:
                continue
            if k not in keys:
                continue
            seen.add(k)
            out.append(k)

    _add(order)
    _add(recommended)
    _add(sorted(keys))
    return out


def _infer_start_block(flow: dict) -> str | None:
    start = flow.get("start_block")
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    if isinstance(start, str) and start in blocks:
        return start
    if blocks:
        return next(iter(blocks.keys()))
    return None


def _infer_end_block(flow: dict) -> str | None:
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    end = flow.get("end_block")
    if isinstance(end, str) and end in blocks:
        return end
    if "end" in blocks:
        return "end"
    if blocks:
        return list(blocks.keys())[-1]
    return None


def _rewrite_block_refs(block: dict[str, Any], mapping: dict[str, str]) -> None:
    def _map_id(val: Any) -> Any:
        if isinstance(val, str) and val in mapping:
            return mapping[val]
        return val

    if isinstance(block.get("next"), str):
        block["next"] = _map_id(block.get("next"))

    next_map = block.get("next_map")
    if isinstance(next_map, dict):
        for k, v in list(next_map.items()):
            next_map[k] = _map_id(v)
        block["next_map"] = next_map

    branches = block.get("branches")
    if isinstance(branches, dict):
        for k, v in list(branches.items()):
            branches[k] = _map_id(v)
        block["branches"] = branches

    if block.get("type") == "condition":
        conditions = block.get("conditions")
        if isinstance(conditions, list):
            for cond in conditions:
                if not isinstance(cond, dict):
                    continue
                cond["next"] = _map_id(cond.get("next"))


def _namespace_flow(flow: dict[str, Any], prefix: str) -> tuple[dict[str, Any], str | None, str | None]:
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    mapping: dict[str, str] = {}
    for bid in blocks.keys():
        mapping[str(bid)] = f"{prefix}::{bid}"

    namespaced_blocks: dict[str, Any] = {}
    for bid, block in blocks.items():
        if not isinstance(block, dict):
            continue
        new_block = copy.deepcopy(block)
        new_id = mapping.get(str(bid), str(bid))
        new_block["id"] = new_id
        _rewrite_block_refs(new_block, mapping)
        namespaced_blocks[new_id] = new_block

    start = _infer_start_block(flow)
    end = _infer_end_block(flow)
    start = mapping.get(start) if start else None
    end = mapping.get(end) if end else None
    return namespaced_blocks, start, end


def _validate_flow_refs(flow: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    if not blocks:
        return ["missing_blocks"]

    ids = set(blocks.keys())
    start = flow.get("start_block")
    if not isinstance(start, str) or start not in ids:
        errors.append("missing_start_block")

    def _check_next(next_id: Any, ctx: str) -> None:
        if next_id is None:
            return
        if not isinstance(next_id, str) or not next_id.strip():
            return
        if next_id not in ids:
            errors.append(f"missing_block_ref:{ctx}:{next_id}")

    for bid, block in blocks.items():
        if not isinstance(block, dict):
            continue
        _check_next(block.get("next"), f"{bid}.next")
        nm = block.get("next_map")
        if isinstance(nm, dict):
            for k, v in nm.items():
                _check_next(v, f"{bid}.next_map[{k}]")
        branches = block.get("branches")
        if isinstance(branches, dict):
            for k, v in branches.items():
                _check_next(v, f"{bid}.branches[{k}]")
        if block.get("type") == "condition":
            conditions = block.get("conditions")
            if isinstance(conditions, list):
                for idx, cond in enumerate(conditions):
                    if not isinstance(cond, dict):
                        continue
                    _check_next(cond.get("next"), f"{bid}.conditions[{idx}].next")

    return errors


def compose_sequential_flow(
    *,
    base_flow: dict[str, Any],
    subflows_by_key: dict[str, dict[str, Any]],
    order: list[str],
    enabled_map: dict[str, bool],
    locks: dict[str, Any],
    overrides_payload: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    keys = list(subflows_by_key.keys())
    chosen = _coalesce_order(order, [], keys)
    if not chosen:
        return None, ["missing_subflows"]

    # Filter enabled (but keep required)
    effective: list[str] = []
    for key in chosen:
        if key not in subflows_by_key:
            continue
        required = _is_required(locks, key)
        enabled_val = enabled_map.get(key, True)
        if not enabled_val and not required:
            continue
        effective.append(key)

    if not effective:
        return None, ["all_subflows_disabled"]

    composed_blocks: dict[str, Any] = {}
    start_block: str | None = None
    prev_end: str | None = None

    for idx, key in enumerate(effective):
        payload = subflows_by_key.get(key)
        if not isinstance(payload, dict):
            continue
        if not isinstance(payload.get("blocks"), dict) or not payload.get("blocks"):
            continue
        if not _subflow_enabled(payload):
            continue

        sf_id = str(payload.get("version") or key)
        sf_flow = copy.deepcopy(payload)

        # Apply safe overrides (if editable)
        if _is_editable(locks, key):
            ov_entry = {}
            overrides = overrides_payload.get("overrides") if isinstance(overrides_payload.get("overrides"), dict) else {}
            if isinstance(overrides, dict):
                file_key = payload.get("__file") or payload.get("_file")
                if isinstance(file_key, str) and file_key in overrides:
                    ov_entry = overrides.get(file_key) if isinstance(overrides.get(file_key), dict) else {}
            if ov_entry:
                sf_flow = apply_overrides_to_flow(sf_flow, ov_entry)

        ns_blocks, ns_start, ns_end = _namespace_flow(sf_flow, sf_id)
        if not ns_blocks:
            continue
        if idx == 0:
            start_block = ns_start or next(iter(ns_blocks.keys()))

        # Link previous end -> current start
        if prev_end and ns_start:
            prev_block = composed_blocks.get(prev_end)
            if isinstance(prev_block, dict):
                prev_block.pop("next_map", None)
                prev_block.pop("branches", None)
                prev_block.pop("conditions", None)
                prev_block["next"] = ns_start
                composed_blocks[prev_end] = prev_block

        composed_blocks.update(ns_blocks)
        prev_end = ns_end or prev_end

    if not composed_blocks or not start_block:
        return None, ["composition_failed"]

    cfg = base_flow.get("config") if isinstance(base_flow.get("config"), dict) else {}
    cfg = copy.deepcopy(cfg)
    cfg.pop("router", None)
    cfg.setdefault("subflows", {})
    if isinstance(cfg.get("subflows"), dict):
        cfg["subflows"]["composition_mode"] = "sequential"
        cfg["subflows"]["order"] = effective

    composed = {
        "version": base_flow.get("version") or "sequential_composed",
        "plan": base_flow.get("plan") or "base",
        "languages": base_flow.get("languages") if isinstance(base_flow.get("languages"), list) else ["es"],
        "composition_mode": "sequential",
        "start_block": start_block,
        "config": cfg,
        "blocks": composed_blocks,
    }

    errors = _validate_flow_refs(composed)
    if errors:
        return None, errors
    return composed, []


def maybe_compose_for_tenant(
    *,
    db: Session,
    tenant: Tenant,
    base_flow: dict[str, Any],
) -> dict[str, Any]:
    vertical_key = getattr(tenant, "vertical_key", None)
    if not vertical_key:
        return base_flow

    overrides_payload = load_overrides_payload(db, str(tenant.id))
    mode = get_composition_mode(overrides_payload)
    if mode == "router":
        # fallback to vertical default if tenant has no explicit preference
        if not overrides_payload.get("composition_mode"):
            mode = _composition_default(vertical_key) or "router"

    if mode != "sequential":
        return base_flow

    scope_key = _resolve_scope_for_tenant(tenant)
    discovered = vertical_list_subflows(str(vertical_key), scope=scope_key, save_to=None)
    subflows_by_key: dict[str, dict[str, Any]] = {}
    for entry in discovered:
        key = str(entry.get("key") or "").strip()
        file_str = str(entry.get("filename") or "").strip()
        if not key or not file_str:
            continue
        payload = vertical_read_asset_json(str(vertical_key), file_str)
        if not isinstance(payload, dict):
            continue
        payload = copy.deepcopy(payload)
        payload["__file"] = file_str
        subflows_by_key[key] = payload

    if not subflows_by_key:
        return base_flow

    order = get_order_list(overrides_payload)
    if not order and isinstance(base_flow.get("subflow_order"), list):
        order = [str(x) for x in base_flow.get("subflow_order") if x]
    if not order:
        order = _recommended_order(vertical_key)

    enabled_map = get_enabled_map(overrides_payload)
    locks = _subflow_locks(vertical_key)

    composed, errors = compose_sequential_flow(
        base_flow=base_flow,
        subflows_by_key=subflows_by_key,
        order=order,
        enabled_map=enabled_map,
        locks=locks,
        overrides_payload=overrides_payload,
    )
    if composed and not errors:
        return composed
    return base_flow
