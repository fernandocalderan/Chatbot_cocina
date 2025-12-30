from __future__ import annotations

import copy
from typing import Any

from sqlalchemy.orm import Session

from app.models.configs import Config


CONFIG_TIPO_SUBFLOW_OVERRIDES = "tenant_subflow_overrides"


def _safe_dict(x: Any) -> dict:
    return x if isinstance(x, dict) else {}


def load_overrides_payload(db: Session, tenant_id: str) -> dict[str, Any]:
    row = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_SUBFLOW_OVERRIDES)
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .first()
    )
    payload = row.payload_json if row else {}
    return payload if isinstance(payload, dict) else {}


def _next_version(db: Session, tenant_id: str) -> int:
    row = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_SUBFLOW_OVERRIDES)
        .order_by(Config.version.desc())
        .first()
    )
    return int(getattr(row, "version", 0) or 0) + 1


def save_overrides_payload(db: Session, tenant_id: str, payload: dict[str, Any]) -> Config:
    cfg = Config(
        tenant_id=tenant_id,
        tipo=CONFIG_TIPO_SUBFLOW_OVERRIDES,
        payload_json=payload,
        version=_next_version(db, tenant_id),
    )
    db.add(cfg)
    db.commit()
    return cfg


def get_overrides_for_file(payload: dict[str, Any], subflow_file: str) -> dict[str, Any]:
    overrides = _safe_dict(payload.get("overrides"))
    entry = overrides.get(subflow_file)
    return entry if isinstance(entry, dict) else {}


def apply_overrides_to_flow(flow_data: dict[str, Any], overrides_entry: dict[str, Any]) -> dict[str, Any]:
    """
    Aplica overrides seguros (solo `text` y `options[].label`) sobre un flow base.
    No permite cambiar estructura: ids, type, next, branches, etc.
    """
    if not isinstance(flow_data, dict) or not flow_data:
        return flow_data
    if not isinstance(overrides_entry, dict) or not overrides_entry:
        return flow_data

    blocks = flow_data.get("blocks") if isinstance(flow_data.get("blocks"), dict) else None
    patch_blocks = overrides_entry.get("blocks") if isinstance(overrides_entry.get("blocks"), dict) else None
    if not isinstance(blocks, dict) or not isinstance(patch_blocks, dict) or not patch_blocks:
        return flow_data

    out = copy.deepcopy(flow_data)
    out_blocks = out.get("blocks") if isinstance(out.get("blocks"), dict) else {}
    langs = out.get("languages") if isinstance(out.get("languages"), list) else []
    default_lang = str(langs[0]) if langs else "es"

    for block_id, patch in patch_blocks.items():
        if not isinstance(block_id, str) or not block_id:
            continue
        if block_id not in out_blocks or not isinstance(out_blocks.get(block_id), dict):
            continue
        if not isinstance(patch, dict):
            continue
        base_block = out_blocks[block_id]

        if isinstance(patch.get("text"), dict):
            current = base_block.get("text")
            if isinstance(current, dict):
                text_obj = current
            elif isinstance(current, str):
                text_obj = {default_lang: current}
            else:
                text_obj = {}
            for k, v in patch["text"].items():
                if v is None:
                    continue
                text_obj[str(k)] = str(v)
            base_block["text"] = text_obj

        if isinstance(patch.get("options"), list) and str(base_block.get("type") or "") in {"buttons", "options"}:
            existing = base_block.get("options") if isinstance(base_block.get("options"), list) else []
            existing_by_id: dict[str, dict] = {}
            for opt in existing:
                if not isinstance(opt, dict):
                    continue
                oid = opt.get("id") if opt.get("id") is not None else opt.get("value")
                if oid is None:
                    continue
                existing_by_id[str(oid)] = opt

            has_branching = isinstance(base_block.get("next_map"), dict) or isinstance(base_block.get("branches"), dict)
            allow_add = (not has_branching) and bool(base_block.get("next"))

            for opt_patch in patch["options"]:
                if not isinstance(opt_patch, dict):
                    continue
                oid = opt_patch.get("id")
                if oid is None:
                    continue
                sid = str(oid).strip()
                if not sid:
                    continue
                label_val = opt_patch.get("label")
                if isinstance(label_val, dict):
                    label_val = {k: str(v) for k, v in label_val.items() if v is not None}
                elif label_val is not None:
                    label_val = str(label_val)

                if sid in existing_by_id:
                    if label_val is not None:
                        existing_by_id[sid]["label"] = label_val
                    continue
                if not allow_add:
                    continue
                if label_val is None:
                    continue
                existing.append({"id": sid, "label": label_val})

            base_block["options"] = existing

        out_blocks[block_id] = base_block

    out["blocks"] = out_blocks
    return out

