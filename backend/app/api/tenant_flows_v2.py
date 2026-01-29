from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme
from app.api.deps import get_db, get_tenant_id
from app.middleware.authz import require_any_role
from app.models.flows import Flow as FlowVersioned
from app.models.tenants import Tenant
from app.services.flow_resolver import resolve_runtime_flow, resolve_active_flow, FlowResolutionError
from app.services.verticals import (
    build_vertical_subflow_filename,
    parse_vertical_router_routes_filename,
    resolve_flow_id,
    tenant_vertical_scopes,
    vertical_flow_base,
    vertical_list_subflows,
)
from app.models.configs import Config
from app.services.ia_usage_service import IAQuotaExceeded
from app.services.flow_generation import generate_flow_draft
from app.services.flow_generation import generation_limit_for_plan, monthly_generation_count
from app.services.subflow_overrides import (
    apply_overrides_to_flow,
    get_overrides_for_file,
    get_composition_mode,
    get_enabled_map,
    get_order_list,
    load_overrides_payload as load_subflow_overrides_payload,
    normalize_composition_mode,
    save_overrides_payload as save_subflow_overrides_payload,
)
from app.services.verticals import (
    vertical_read_asset_json,
    vertical_subflow_composition_default,
    vertical_subflow_locks,
    vertical_subflow_recommended_order,
)


router = APIRouter(prefix="/tenant/flows", tags=["tenant-flows-v2"])

CONFIG_TIPO_MATERIALS = "tenant_flow_materials"
CONFIG_TIPO_SUBFLOWS = "tenant_subflow_overrides"


def _slugify_key(value: object) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    out = []
    for ch in raw:
        if ("a" <= ch <= "z") or ("0" <= ch <= "9") or ch in {"_", "-"}:
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_-")

def _infer_router_cfg_from_flow(flow: dict) -> dict | None:
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    if not blocks:
        return None

    candidates: list[tuple[str, str, bool]] = []
    for bid, block in blocks.items():
        if not isinstance(block, dict):
            continue
        btype = str(block.get("type") or "").strip().lower()
        if btype not in {"buttons", "options"}:
            continue
        options = block.get("options")
        if not isinstance(options, list) or not options:
            continue
        save_to = block.get("save_to") if isinstance(block.get("save_to"), str) else None
        if not save_to or not save_to.strip():
            continue
        next_is_end = str(block.get("next") or "").strip().lower() == "end"
        candidates.append((str(bid), str(save_to).strip(), next_is_end))

    if not candidates:
        return None
    # Prefer the v1-safe router pattern (ends in `end`) when possible.
    candidates = sorted(candidates, key=lambda x: (not x[2], x[0]))
    block_id, save_to, _ = candidates[0]
    return {"block_id": block_id, "save_to": save_to, "mode": "handoff_end"}


def _resolve_router_cfg_for_tenant(db: Session, tenant: Tenant, runtime_flow: dict) -> dict | None:
    cfg = runtime_flow.get("config") if isinstance(runtime_flow.get("config"), dict) else {}
    router_cfg = cfg.get("router") if isinstance(cfg.get("router"), dict) else None
    if isinstance(router_cfg, dict) and str(router_cfg.get("save_to") or "").strip():
        return router_cfg

    # Fallback: take router metadata from scope base (helps with older published flows missing config.router)
    scopes = tenant_vertical_scopes(tenant)
    base = vertical_flow_base(getattr(tenant, "vertical_key", None), scopes)
    base_cfg = base.get("config") if isinstance(base, dict) and isinstance(base.get("config"), dict) else {}
    base_router = base_cfg.get("router") if isinstance(base_cfg.get("router"), dict) else None
    if isinstance(base_router, dict) and str(base_router.get("save_to") or "").strip():
        return base_router

    # Last resort: infer from runtime blocks.
    return _infer_router_cfg_from_flow(runtime_flow)


def _flow_router_and_routes_for_tenant(db: Session, tenant: Tenant) -> tuple[dict | None, dict | None, dict]:
    """
    Devuelve (runtime_flow, router_cfg?, routes_payload{}).
    """
    plan_value = getattr(tenant, "plan", "base")
    if hasattr(plan_value, "value"):
        plan_value = plan_value.value
    try:
        flow = resolve_runtime_flow(db=db, tenant=tenant, flow_id_override=None, plan_value=str(plan_value or "base").lower())
    except FlowResolutionError as exc:
        raise HTTPException(status_code=409, detail=exc.code)
    if not isinstance(flow, dict) or not flow:
        return None, None, {}
    vertical_key = getattr(tenant, "vertical_key", None)
    if not vertical_key:
        return flow, None, {}

    router_cfg = _resolve_router_cfg_for_tenant(db, tenant, flow)
    routes_file = str(router_cfg.get("routes_file") or "").strip() if isinstance(router_cfg, dict) else ""
    routes_payload: dict = {}
    if isinstance(router_cfg, dict) and routes_file:
        loaded = vertical_read_asset_json(str(vertical_key), routes_file)
        routes_payload = loaded if isinstance(loaded, dict) else {}
    return flow, router_cfg, routes_payload


def _router_scope_for_tenant(tenant: Tenant, router_cfg: dict | None) -> str | None:
    scope_key = str((router_cfg or {}).get("scope") or "").strip().lower() or None
    if scope_key:
        return scope_key
    routes_file = str((router_cfg or {}).get("routes_file") or "").strip()
    parsed = parse_vertical_router_routes_filename(routes_file) if routes_file else None
    if isinstance(parsed, dict) and parsed.get("scope"):
        return str(parsed["scope"]).strip().lower()
    scopes = tenant_vertical_scopes(tenant)
    return str(scopes[0]).strip().lower() if scopes else None


def _subflow_enabled(payload: dict) -> bool:
    cfg = payload.get("config") if isinstance(payload.get("config"), dict) else {}
    meta = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
    if meta.get("disabled") is True:
        return False
    if meta.get("enabled") is False:
        return False
    return True


def _resolve_subflow_file(
    *,
    vertical_key: str,
    scope_key: str | None,
    save_to: str,
    key: str,
    routes_payload: dict,
) -> tuple[str | None, str | None]:
    # 1) Colección abierta del scope por convención de nombre
    if scope_key:
        filename = build_vertical_subflow_filename(scope=scope_key, save_to=save_to, key=key)
        payload = vertical_read_asset_json(vertical_key, filename)
        if isinstance(payload, dict) and isinstance(payload.get("blocks"), dict) and payload.get("blocks") and _subflow_enabled(payload):
            return filename, str(payload.get("version") or "") or None

    # 2) Compat/alias: mapping legacy (si existe)
    file_from_routes, subflow_id = _subflow_file_from_routes(routes_payload, key)
    if isinstance(file_from_routes, str) and file_from_routes.strip():
        return file_from_routes.strip(), subflow_id

    return None, None


def _subflow_file_from_routes(routes_payload: dict, key: str) -> tuple[str | None, str | None]:
    routes = routes_payload.get("routes") if isinstance(routes_payload.get("routes"), dict) else {}
    picked = routes.get(key)
    if picked is None:
        picked = routes_payload.get("default")
    if isinstance(picked, str):
        return picked, None
    if isinstance(picked, dict):
        return (picked.get("file") or picked.get("filename")), (picked.get("subflow_id") or picked.get("flow_id"))
    return None, None


def _resolve_sequential_subflow_file(
    *,
    vertical_key: str,
    scope_key: str | None,
    key: str,
) -> tuple[str | None, str | None]:
    discovered = vertical_list_subflows(str(vertical_key), scope=scope_key, save_to=None)
    for entry in discovered:
        k = _slugify_key(entry.get("key")) or str(entry.get("key") or "").strip()
        if k != key:
            continue
        file_str = str(entry.get("filename") or "").strip()
        if not file_str:
            continue
        base = vertical_read_asset_json(str(vertical_key), file_str)
        if not isinstance(base, dict) or not isinstance(base.get("blocks"), dict) or not base.get("blocks"):
            return None, None
        return file_str, str(base.get("version") or "") or None
    return None, None


def _subflow_lock_flags(locks: dict[str, Any], key: str) -> tuple[bool, bool]:
    entry = locks.get(key) if isinstance(locks, dict) else None
    if not isinstance(entry, dict):
        return False, False
    required = bool(entry.get("required"))
    locked = bool(entry.get("locked") or (entry.get("editable") is False))
    return required, locked


def _sanitize_overrides(overrides: dict[str, Any], allowed_files: set[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for file_key, entry in overrides.items():
        if file_key not in allowed_files or not isinstance(entry, dict):
            continue
        blocks = entry.get("blocks")
        if not isinstance(blocks, dict):
            continue
        cleaned_blocks: dict[str, Any] = {}
        for block_id, patch in blocks.items():
            if not isinstance(block_id, str) or not isinstance(patch, dict):
                continue
            safe_patch: dict[str, Any] = {}
            if isinstance(patch.get("text"), dict):
                safe_patch["text"] = {str(k): str(v) for k, v in patch.get("text", {}).items() if v is not None}
            if isinstance(patch.get("text_enriched"), dict):
                safe_patch["text_enriched"] = {str(k): str(v) for k, v in patch.get("text_enriched", {}).items() if v is not None}
            if isinstance(patch.get("text_variants"), list):
                safe_patch["text_variants"] = [str(v) for v in patch.get("text_variants") if v is not None]
            if isinstance(patch.get("options"), list):
                opts_out: list[dict[str, Any]] = []
                for opt in patch.get("options") or []:
                    if not isinstance(opt, dict):
                        continue
                    oid = opt.get("id")
                    if oid is None:
                        continue
                    label_val = opt.get("label")
                    if isinstance(label_val, dict):
                        label_val = {str(k): str(v) for k, v in label_val.items() if v is not None}
                    elif label_val is not None:
                        label_val = str(label_val)
                    opts_out.append({"id": str(oid), "label": label_val})
                safe_patch["options"] = opts_out
            if safe_patch:
                cleaned_blocks[block_id] = safe_patch
        if cleaned_blocks:
            out[file_key] = {"blocks": cleaned_blocks}
    return out


def _router_labels(flow: dict, router_cfg: dict) -> dict[str, Any]:
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    block_id = str(router_cfg.get("block_id") or "").strip()
    router_block = blocks.get(block_id) if block_id else None
    opts = router_block.get("options") if isinstance(router_block, dict) and isinstance(router_block.get("options"), list) else []
    out: dict[str, Any] = {}
    for opt in opts:
        if not isinstance(opt, dict):
            continue
        oid = opt.get("id") if opt.get("id") is not None else opt.get("value")
        if oid is None:
            continue
        k = _slugify_key(oid) or _slugify_key(opt.get("value")) or _slugify_key(opt.get("label"))
        if not k:
            continue
        out[k] = opt.get("label") or opt.get("value") or opt.get("id") or k
    return out


def _load_published_materials(db: Session, tenant_id: str) -> dict | None:
    rows = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .all()
    )
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() == "PUBLISHED":
            return payload if isinstance(payload, dict) else None
    return None


def _active_or_latest_published_flow(db: Session, tenant: Tenant) -> FlowVersioned | None:
    active_id = getattr(tenant, "active_flow_id", None)
    if active_id:
        row = (
            db.query(FlowVersioned)
            .filter(FlowVersioned.id == active_id, FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "published")
            .first()
        )
        if row:
            return row
    return (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "published")
        .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
        .first()
    )


def _latest_draft_flow(db: Session, tenant: Tenant) -> FlowVersioned | None:
    return (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "draft")
        .order_by(FlowVersioned.updated_at.desc(), FlowVersioned.version.desc())
        .first()
    )


def _next_version(db: Session, tenant: Tenant) -> int:
    latest = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    return (latest.version + 1) if latest else 1


def _ensure_flow_system_v2(db: Session, tenant: Tenant) -> None:
    branding = getattr(tenant, "branding", {}) or {}
    if str(branding.get("flow_system") or "").strip().lower() != "v2":
        branding["flow_system"] = "v2"
        tenant.branding = branding
        db.add(tenant)


class TextPatch(BaseModel):
    es: str | None = None
    en: str | None = None
    pt: str | None = None
    ca: str | None = None


class OptionPatch(BaseModel):
    id: str = Field(..., description="ID estable de la opción (no visible para el usuario)")
    label: TextPatch | str = Field(..., description="Label visible (multi-idioma o string)")


class BlockPatchInput(BaseModel):
    text: TextPatch | None = None
    text_enriched: TextPatch | None = None
    text_variants: list[str] | None = None
    options: list[OptionPatch] | None = None


class BlockBatchPatch(BlockPatchInput):
    block_id: str = Field(..., min_length=1, max_length=120)


class BatchPatchInput(BaseModel):
    patches: list[BlockBatchPatch] = Field(default_factory=list)


class PublishInput(BaseModel):
    use_draft: bool = True


class GenerateInput(BaseModel):
    allow_overage: bool = False
    languages: list[str] | None = None


class SubflowListItem(BaseModel):
    key: str
    label: Any | None = None
    file: str
    subflow_id: str | None = None
    has_overrides: bool = False
    enabled: bool | None = None
    required: bool | None = None
    locked: bool | None = None


class SubflowsUpdateInput(BaseModel):
    composition_mode: str | None = None
    order: list[str] | None = None
    enabled: dict[str, bool] | None = None
    overrides: dict[str, Any] | None = None


@router.get("/quota", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def get_flow_generation_quota(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")
    limit = generation_limit_for_plan(getattr(tenant, "plan", None))
    used = monthly_generation_count(db, str(tenant.id))
    return {"tenant_id": str(tenant.id), "limit": int(limit), "used": int(used), "remaining": int(max(limit - used, 0))}


@router.post("/generate", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def generate_flow(
    payload: GenerateInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")
    try:
        return generate_flow_draft(
            db=db,
            tenant=tenant,
            allow_overage=bool(payload.allow_overage),
            languages=payload.languages,
            user_id=None,
        )
    except IAQuotaExceeded as exc:
        msg = str(exc) or "ia_quota_exceeded"
        if "ia_disabled_for_tenant" in msg:
            raise HTTPException(status_code=403, detail="ia_disabled_for_tenant")
        raise HTTPException(status_code=402, detail=msg)
    except ValueError as exc:
        code = str(exc) or "flow_generate_failed"
        if code in {"missing_openai_api_key", "invalid_openai_api_key", "ia_provider_unavailable"}:
            raise HTTPException(status_code=503, detail=code)
        if code == "ia_rate_limited":
            raise HTTPException(status_code=429, detail=code)
        raise HTTPException(status_code=400, detail=code)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc) or "flow_generate_failed")


@router.get("/published", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def get_published_flow(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    try:
        row = resolve_active_flow(db, str(tenant.id))
    except FlowResolutionError as exc:
        raise HTTPException(status_code=409, detail=exc.code)
    return {
        "tenant_id": str(tenant.id),
        "flow_system": (getattr(tenant, "branding", {}) or {}).get("flow_system") or "v1",
        "published": {
            "flow_id": str(row.id),
            "version": row.version,
            "published_at": row.published_at.isoformat() if row.published_at else None,
        },
        "flow": row.schema_json if isinstance(row.schema_json, dict) else {},
    }


@router.get("/draft", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def get_draft_flow(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    row = _latest_draft_flow(db, tenant)
    return {
        "tenant_id": str(tenant.id),
        "draft": (
            {"flow_id": str(row.id), "version": row.version, "updated_at": row.updated_at.isoformat() if row.updated_at else None}
            if row
            else None
        ),
        "flow": row.schema_json if (row and isinstance(row.schema_json, dict)) else {},
    }


@router.post("/draft/reset", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def reset_draft_from_current_runtime(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    """
    Crea un draft desde el flow base del scope principal (estructura fija).
    Útil cuando el tenant todavía no puede/usa IA.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    scopes = tenant_vertical_scopes(tenant)
    base = vertical_flow_base(getattr(tenant, "vertical_key", None), scopes)
    if not isinstance(base, dict) or not base:
        # Compat: si el tenant no tiene vertical/scopes configurados todavía, usa el flow efectivo.
        materials = _load_published_materials(db, str(tenant.id))
        flow_id_override = materials.get("flow_id") if isinstance(materials, dict) else None
        flow_id_override = resolve_flow_id(flow_id_override, getattr(tenant, "vertical_key", None))
        plan_value = getattr(tenant, "plan", "base")
        if hasattr(plan_value, "value"):
            plan_value = plan_value.value
        try:
            flow_data = resolve_runtime_flow(
                db=db,
                tenant=tenant,
                flow_id_override=flow_id_override,
                plan_value=str(plan_value or "base").lower(),
            )
        except FlowResolutionError as exc:
            raise HTTPException(status_code=409, detail=exc.code)
        if not isinstance(flow_data, dict) or not flow_data:
            raise HTTPException(status_code=400, detail="missing_flow_base_for_scope")
        base = flow_data

    # Create a new draft version (do not overwrite existing published history).
    new_flow = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(getattr(tenant, "vertical_key", "") or "") or None,
        scope_key=(scopes[0] if scopes else None),
        version=_next_version(db, tenant),
        schema_json=base,
        estado="draft",
        published_at=None,
        owner_type="TENANT",
        owner_id=tenant.id,
        flow_kind="base",
    )
    db.add(new_flow)
    _ensure_flow_system_v2(db, tenant)
    db.commit()
    return {"tenant_id": str(tenant.id), "flow_id": str(new_flow.id), "version": new_flow.version, "estado": new_flow.estado}


@router.patch("/draft/blocks/{block_id}", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def patch_draft_block(
    block_id: str,
    payload: BlockPatchInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    draft = _latest_draft_flow(db, tenant)
    if not draft or not isinstance(draft.schema_json, dict):
        raise HTTPException(status_code=404, detail="draft_not_found")

    flow = draft.schema_json
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else None
    if not isinstance(blocks, dict) or block_id not in blocks or not isinstance(blocks.get(block_id), dict):
        raise HTTPException(status_code=404, detail="block_not_found")

    block = blocks[block_id]

    # Text patch (multi-idioma)
    if payload.text is not None:
        text_obj: dict[str, Any] = block.get("text") if isinstance(block.get("text"), dict) else {}
        patch = payload.text.model_dump(exclude_none=True)
        for k, v in patch.items():
            if v is not None:
                text_obj[k] = v
        block["text"] = text_obj

    if payload.text_enriched is not None:
        text_obj: dict[str, Any] = block.get("text_enriched") if isinstance(block.get("text_enriched"), dict) else {}
        patch = payload.text_enriched.model_dump(exclude_none=True)
        for k, v in patch.items():
            if v is not None:
                text_obj[k] = v
        block["text_enriched"] = text_obj

    if payload.text_variants is not None:
        block["text_variants"] = [str(v) for v in payload.text_variants if v is not None]

    # Options patch (labels; and optionally add options in safe blocks)
    if payload.options is not None:
        if block.get("type") not in {"buttons", "options"}:
            raise HTTPException(status_code=400, detail="block_not_options")
        existing = block.get("options") if isinstance(block.get("options"), list) else []
        existing_ids: list[str] = []
        existing_by_id: dict[str, dict] = {}
        for opt in existing:
            if not isinstance(opt, dict):
                continue
            oid = opt.get("id") or opt.get("value")
            if oid is None:
                continue
            sid = str(oid)
            existing_ids.append(sid)
            existing_by_id[sid] = opt

        has_branching = isinstance(block.get("next_map"), dict) or isinstance(block.get("branches"), dict)
        allow_add = (not has_branching) and bool(block.get("next"))

        for opt_patch in payload.options:
            oid = str(opt_patch.id).strip()
            if not oid:
                continue
            label_val: Any
            if isinstance(opt_patch.label, TextPatch):
                label_val = opt_patch.label.model_dump(exclude_none=True)
            else:
                label_val = str(opt_patch.label)

            if oid in existing_by_id:
                existing_by_id[oid]["label"] = label_val
                continue
            if not allow_add:
                raise HTTPException(status_code=400, detail="cannot_add_options_on_branching_block")
            # Add option (non-branching: all options advance to same `next`)
            existing.append({"id": oid, "label": label_val})

        block["options"] = existing

    blocks[block_id] = block
    flow["blocks"] = blocks
    draft.schema_json = flow
    db.add(draft)
    db.commit()
    return {"tenant_id": str(tenant.id), "flow_id": str(draft.id), "version": draft.version, "block_id": block_id}


@router.patch("/draft/blocks", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def patch_draft_blocks_batch(
    payload: BatchPatchInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    """
    Batch patch: permite aplicar múltiples cambios (texto/opciones) en un solo commit.
    - Si cualquier patch falla, no se persiste nada (operación atómica).
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    patches = payload.patches if isinstance(payload, BatchPatchInput) else []
    if not isinstance(patches, list) or not patches:
        raise HTTPException(status_code=400, detail="missing_patches")
    if len(patches) > 200:
        raise HTTPException(status_code=400, detail="too_many_patches")

    draft = _latest_draft_flow(db, tenant)
    if not draft or not isinstance(draft.schema_json, dict):
        raise HTTPException(status_code=404, detail="draft_not_found")

    flow = draft.schema_json
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else None
    if not isinstance(blocks, dict) or not blocks:
        raise HTTPException(status_code=400, detail="invalid_flow_blocks")

    # Apply all patches to in-memory copy first (atomic)
    updated_ids: list[str] = []
    for patch in patches:
        block_id = str(getattr(patch, "block_id", "") or "").strip()
        if not block_id:
            raise HTTPException(status_code=400, detail="invalid_block_id")
        if block_id not in blocks or not isinstance(blocks.get(block_id), dict):
            raise HTTPException(status_code=404, detail=f"block_not_found:{block_id}")

        block = blocks[block_id]

        # Text patch (multi-idioma)
        if patch.text is not None:
            text_obj: dict[str, Any] = block.get("text") if isinstance(block.get("text"), dict) else {}
            patch_text = patch.text.model_dump(exclude_none=True)
            for k, v in patch_text.items():
                if v is not None:
                    text_obj[k] = v
            block["text"] = text_obj

        # Options patch (labels; and optionally add options in safe blocks)
        if patch.options is not None:
            if block.get("type") not in {"buttons", "options"}:
                raise HTTPException(status_code=400, detail=f"block_not_options:{block_id}")
            existing = block.get("options") if isinstance(block.get("options"), list) else []
            existing_by_id: dict[str, dict] = {}
            for opt in existing:
                if not isinstance(opt, dict):
                    continue
                oid = opt.get("id") or opt.get("value")
                if oid is None:
                    continue
                existing_by_id[str(oid)] = opt

            has_branching = isinstance(block.get("next_map"), dict) or isinstance(block.get("branches"), dict)
            allow_add = (not has_branching) and bool(block.get("next"))

            for opt_patch in patch.options:
                oid = str(opt_patch.id).strip()
                if not oid:
                    continue
                label_val: Any
                if isinstance(opt_patch.label, TextPatch):
                    label_val = opt_patch.label.model_dump(exclude_none=True)
                else:
                    label_val = str(opt_patch.label)

                if oid in existing_by_id:
                    existing_by_id[oid]["label"] = label_val
                    continue
                if not allow_add:
                    raise HTTPException(status_code=400, detail=f"cannot_add_options_on_branching_block:{block_id}")
                existing.append({"id": oid, "label": label_val})

            block["options"] = existing

        blocks[block_id] = block
        updated_ids.append(block_id)

    flow["blocks"] = blocks
    draft.schema_json = flow
    db.add(draft)
    db.commit()
    return {
        "tenant_id": str(tenant.id),
        "flow_id": str(draft.id),
        "version": draft.version,
        "updated_blocks": sorted(set(updated_ids)),
        "count": len(updated_ids),
    }


@router.post("/publish", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def publish_draft(
    payload: PublishInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    draft = _latest_draft_flow(db, tenant)
    if not draft or not isinstance(draft.schema_json, dict):
        raise HTTPException(status_code=404, detail="draft_not_found")

    now = datetime.now(timezone.utc)
    # Unpublish previous published flows for this tenant
    db.query(FlowVersioned).filter(
        FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "published"
    ).update({"estado": "draft", "published_at": None})
    published = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(getattr(tenant, "vertical_key", "") or "") or None,
        scope_key=(scopes[0] if scopes else None),
        version=_next_version(db, tenant),
        schema_json=draft.schema_json,
        estado="published",
        published_at=now,
        owner_type="TENANT",
        owner_id=tenant.id,
        flow_kind="base",
    )
    db.add(published)
    db.flush()

    tenant.active_flow_id = published.id
    branding = getattr(tenant, "branding", {}) or {}
    branding["custom_flow_enabled"] = True
    branding["flow_system"] = "v2"
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    return {"tenant_id": str(tenant.id), "flow_id": str(published.id), "version": published.version, "estado": published.estado}


@router.get("/subflows", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def list_subflows(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    vertical_key = getattr(tenant, "vertical_key", None)
    if not vertical_key:
        return {"tenant_id": str(tenant.id), "router": None, "subflows": []}

    overrides_payload = load_subflow_overrides_payload(db, str(tenant.id))
    composition_mode = get_composition_mode(overrides_payload)
    if not overrides_payload.get("composition_mode"):
        composition_mode = vertical_subflow_composition_default(str(vertical_key)) or "router"

    enabled_map = get_enabled_map(overrides_payload)
    order = get_order_list(overrides_payload)
    recommended_order = vertical_subflow_recommended_order(str(vertical_key))
    locks = vertical_subflow_locks(str(vertical_key))

    items: list[SubflowListItem] = []

    if composition_mode == "sequential":
        scope_key = _router_scope_for_tenant(tenant, None) or "default"
        discovered = vertical_list_subflows(str(vertical_key), scope=scope_key, save_to=None)
        for entry in discovered:
            key = _slugify_key(entry.get("key")) or str(entry.get("key") or "").strip()
            file_str = str(entry.get("filename") or "").strip()
            if not key or not file_str:
                continue
            base = vertical_read_asset_json(str(vertical_key), file_str)
            if not isinstance(base, dict) or not isinstance(base.get("blocks"), dict) or not base.get("blocks") or not _subflow_enabled(base):
                continue
            cfg = base.get("config") if isinstance(base.get("config"), dict) else {}
            sub_meta = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
            label = sub_meta.get("label") or key
            has_ov = bool(isinstance(overrides_payload.get("overrides"), dict) and overrides_payload.get("overrides", {}).get(file_str))
            lock = locks.get(key) if isinstance(locks, dict) else None
            required = bool(lock.get("required")) if isinstance(lock, dict) else False
            locked = bool(lock.get("locked") or (lock.get("editable") is False)) if isinstance(lock, dict) else False
            enabled_val = enabled_map.get(key, True)
            if required:
                enabled_val = True
            items.append(
                SubflowListItem(
                    key=key,
                    label=label,
                    file=file_str,
                    subflow_id=str(base.get("version") or "") or None,
                    has_overrides=has_ov,
                    enabled=enabled_val,
                    required=required,
                    locked=locked,
                )
            )
        # Order by explicit order -> recommended -> key
        order_keys = []
        if isinstance(order, list):
            order_keys.extend([_slugify_key(k) or str(k) for k in order if k])
        if not order_keys:
            order_keys.extend([_slugify_key(k) or str(k) for k in recommended_order if k])
        if order_keys:
            items = sorted(items, key=lambda x: (order_keys.index(x.key) if x.key in order_keys else 10_000, x.key))
        else:
            items = sorted(items, key=lambda x: x.key)

        return {
            "tenant_id": str(tenant.id),
            "composition_mode": "sequential",
            "order": order or [],
            "recommended_order": recommended_order or [],
            "router": None,
            "subflows": [i.model_dump() for i in items],
        }

    # Router mode (default, backward compatible)
    flow, router_cfg, routes_payload = _flow_router_and_routes_for_tenant(db, tenant)
    if not flow:
        return {"tenant_id": str(tenant.id), "router": None, "subflows": []}

    effective_router_cfg = router_cfg if isinstance(router_cfg, dict) else None
    save_to = str((effective_router_cfg or {}).get("save_to") or "").strip()
    if not save_to:
        inferred = _infer_router_cfg_from_flow(flow)
        effective_router_cfg = inferred if isinstance(inferred, dict) else None
        save_to = str((effective_router_cfg or {}).get("save_to") or "").strip()
    if not save_to:
        return {"tenant_id": str(tenant.id), "router": None, "subflows": []}

    scope_key = _router_scope_for_tenant(tenant, effective_router_cfg)
    labels = _router_labels(flow, effective_router_cfg or {})
    overrides = overrides_payload.get("overrides") if isinstance(overrides_payload.get("overrides"), dict) else {}

    discovered = vertical_list_subflows(str(vertical_key), scope=scope_key, save_to=str(save_to).strip().lower())
    for entry in discovered:
        key = _slugify_key(entry.get("key")) or str(entry.get("key") or "").strip()
        file_str = str(entry.get("filename") or "").strip()
        if not key or not file_str:
            continue
        base = vertical_read_asset_json(str(vertical_key), file_str)
        if not isinstance(base, dict) or not isinstance(base.get("blocks"), dict) or not base.get("blocks") or not _subflow_enabled(base):
            continue
        cfg = base.get("config") if isinstance(base.get("config"), dict) else {}
        sub_meta = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
        label = labels.get(key) or sub_meta.get("label") or key
        has_ov = bool(isinstance(overrides, dict) and overrides.get(file_str))
        lock = locks.get(key) if isinstance(locks, dict) else None
        required = bool(lock.get("required")) if isinstance(lock, dict) else False
        locked = bool(lock.get("locked") or (lock.get("editable") is False)) if isinstance(lock, dict) else False
        enabled_val = enabled_map.get(key, True)
        if required:
            enabled_val = True
        items.append(
            SubflowListItem(
                key=key,
                label=label,
                file=file_str,
                subflow_id=str(base.get("version") or "") or None,
                has_overrides=has_ov,
                enabled=enabled_val,
                required=required,
                locked=locked,
            )
        )

    # Compat: incluir también entradas del routes_file que apunten a archivos no canónicos
    routes = routes_payload.get("routes") if isinstance(routes_payload.get("routes"), dict) else {}
    for raw_key in list(routes.keys()):
        if not isinstance(raw_key, str) or not raw_key:
            continue
        key = _slugify_key(raw_key) or raw_key
        subflow_file, subflow_id = _subflow_file_from_routes(routes_payload, key)
        if not subflow_file:
            continue
        file_str = str(subflow_file).strip()
        if not file_str or any(i.key == key and i.file == file_str for i in items):
            continue
        base = vertical_read_asset_json(str(vertical_key), file_str)
        if not isinstance(base, dict) or not isinstance(base.get("blocks"), dict) or not base.get("blocks") or not _subflow_enabled(base):
            continue
        cfg = base.get("config") if isinstance(base.get("config"), dict) else {}
        sub_meta = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
        label = labels.get(key) or sub_meta.get("label") or key
        has_ov = bool(isinstance(overrides, dict) and overrides.get(file_str))
        lock = locks.get(key) if isinstance(locks, dict) else None
        required = bool(lock.get("required")) if isinstance(lock, dict) else False
        locked = bool(lock.get("locked") or (lock.get("editable") is False)) if isinstance(lock, dict) else False
        enabled_val = enabled_map.get(key, True)
        if required:
            enabled_val = True
        items.append(
            SubflowListItem(
                key=key,
                label=label,
                file=file_str,
                subflow_id=str(subflow_id) if subflow_id else (str(base.get("version") or "") or None),
                has_overrides=has_ov,
                enabled=enabled_val,
                required=required,
                locked=locked,
            )
        )

    items = sorted(items, key=lambda x: x.key)
    return {
        "tenant_id": str(tenant.id),
        "composition_mode": "router",
        "order": order or [],
        "recommended_order": recommended_order or [],
        "router": {
            "block_id": str((effective_router_cfg or {}).get("block_id") or ""),
            "save_to": str((effective_router_cfg or {}).get("save_to") or ""),
            "routes_file": str((effective_router_cfg or {}).get("routes_file") or ""),
        },
        "subflows": [i.model_dump() for i in items],
    }


@router.put("/subflows", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def update_subflows(
    payload: SubflowsUpdateInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    vertical_key = getattr(tenant, "vertical_key", None)
    if not vertical_key:
        raise HTTPException(status_code=400, detail="tenant_missing_vertical")

    overrides_payload = load_subflow_overrides_payload(db, str(tenant.id))
    overrides_payload = overrides_payload if isinstance(overrides_payload, dict) else {}

    scope_key = _router_scope_for_tenant(tenant, None) or "default"
    discovered = vertical_list_subflows(str(vertical_key), scope=scope_key, save_to=None)
    catalog_keys: set[str] = set()
    allowed_files: set[str] = set()
    for entry in discovered:
        key = _slugify_key(entry.get("key")) or str(entry.get("key") or "").strip()
        file_str = str(entry.get("filename") or "").strip()
        if key:
            catalog_keys.add(key)
        if file_str:
            allowed_files.add(file_str)

    locks = vertical_subflow_locks(str(vertical_key))

    if payload.composition_mode is not None:
        overrides_payload["composition_mode"] = normalize_composition_mode(payload.composition_mode)

    if payload.order is not None:
        if not isinstance(payload.order, list):
            raise HTTPException(status_code=400, detail="invalid_order")
        order = [_slugify_key(k) or str(k) for k in payload.order if k]
        invalid = [k for k in order if k not in catalog_keys]
        if invalid:
            raise HTTPException(status_code=400, detail="invalid_subflow_in_order")
        # Ensure required subflows are present
        for k, v in (locks or {}).items():
            if isinstance(v, dict) and v.get("required") and k not in order:
                order.append(k)
        overrides_payload["order"] = order

    if payload.enabled is not None:
        if not isinstance(payload.enabled, dict):
            raise HTTPException(status_code=400, detail="invalid_enabled")
        enabled_map = get_enabled_map(overrides_payload)
        for raw_key, raw_val in payload.enabled.items():
            key = _slugify_key(raw_key) or str(raw_key)
            if key not in catalog_keys:
                raise HTTPException(status_code=400, detail="invalid_subflow_in_enabled")
            required, _locked = _subflow_lock_flags(locks, key)
            if required and not bool(raw_val):
                continue
            enabled_map[key] = bool(raw_val)
        # Ensure required subflows are enabled
        for k, v in (locks or {}).items():
            if isinstance(v, dict) and v.get("required"):
                enabled_map[str(k)] = True
        overrides_payload["enabled"] = enabled_map

    if payload.overrides is not None:
        if not isinstance(payload.overrides, dict):
            raise HTTPException(status_code=400, detail="invalid_overrides")
        overrides_payload["overrides"] = _sanitize_overrides(payload.overrides, allowed_files)

    cfg = save_subflow_overrides_payload(db, str(tenant.id), overrides_payload)
    return {
        "tenant_id": str(tenant.id),
        "config_id": str(cfg.id),
        "version": int(cfg.version),
        "composition_mode": overrides_payload.get("composition_mode"),
    }


@router.get("/subflows/preview", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def preview_subflows(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")
    plan_value = getattr(tenant, "plan", "base")
    if hasattr(plan_value, "value"):
        plan_value = plan_value.value
    try:
        flow = resolve_runtime_flow(
            db=db,
            tenant=tenant,
            flow_id_override=None,
            plan_value=str(plan_value or "base").lower(),
        )
    except FlowResolutionError as exc:
        raise HTTPException(status_code=409, detail=exc.code)
    overrides_payload = load_subflow_overrides_payload(db, str(tenant.id))
    composition_mode = get_composition_mode(overrides_payload)
    vertical_key = getattr(tenant, "vertical_key", None)
    if not overrides_payload.get("composition_mode") and vertical_key:
        composition_mode = vertical_subflow_composition_default(str(vertical_key)) or composition_mode
    return {
        "tenant_id": str(tenant.id),
        "composition_mode": composition_mode,
        "flow": flow,
    }


@router.get("/subflows/{subflow_key}", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def get_subflow(
    subflow_key: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    key = _slugify_key(subflow_key) or subflow_key
    vertical_key = getattr(tenant, "vertical_key", None)
    if not vertical_key:
        raise HTTPException(status_code=400, detail="tenant_missing_vertical")
    overrides_payload = load_subflow_overrides_payload(db, str(tenant.id))
    composition_mode = get_composition_mode(overrides_payload)
    if not overrides_payload.get("composition_mode"):
        composition_mode = vertical_subflow_composition_default(str(vertical_key)) or "router"

    subflow_file = None
    subflow_id = None
    scope_key = None
    if composition_mode == "sequential":
        scope_key = _router_scope_for_tenant(tenant, None) or "default"
        subflow_file, subflow_id = _resolve_sequential_subflow_file(
            vertical_key=str(vertical_key), scope_key=scope_key, key=key
        )
    else:
        flow, router_cfg, routes_payload = _flow_router_and_routes_for_tenant(db, tenant)
        if not flow:
            raise HTTPException(status_code=404, detail="router_not_configured")
        effective_router_cfg = router_cfg if isinstance(router_cfg, dict) else _infer_router_cfg_from_flow(flow)
        save_to = str((effective_router_cfg or {}).get("save_to") or "").strip().lower()
        if not save_to:
            raise HTTPException(status_code=404, detail="router_not_configured")
        scope_key = _router_scope_for_tenant(tenant, effective_router_cfg)
        subflow_file, subflow_id = _resolve_subflow_file(
            vertical_key=str(vertical_key),
            scope_key=scope_key,
            save_to=save_to,
            key=key,
            routes_payload=routes_payload,
        )
    if not subflow_file:
        raise HTTPException(status_code=404, detail="subflow_not_found")

    base = vertical_read_asset_json(str(vertical_key), str(subflow_file))
    if not isinstance(base, dict) or not isinstance(base.get("blocks"), dict) or not base.get("blocks"):
        raise HTTPException(status_code=404, detail="subflow_file_not_found")
    if not _subflow_enabled(base):
        raise HTTPException(status_code=404, detail="subflow_disabled")

    overrides_payload = load_subflow_overrides_payload(db, str(tenant.id))
    ov_entry = get_overrides_for_file(overrides_payload, str(subflow_file))
    effective = apply_overrides_to_flow(base, ov_entry)
    locks = vertical_subflow_locks(str(vertical_key))
    required, locked = _subflow_lock_flags(locks, key)

    return {
        "tenant_id": str(tenant.id),
        "key": key,
        "subflow_id": str(subflow_id) if subflow_id else None,
        "file": str(subflow_file),
        "base": base,
        "effective": effective,
        "has_overrides": bool(ov_entry),
        "required": required,
        "locked": locked,
        "composition_mode": composition_mode,
    }


@router.patch("/subflows/{subflow_key}/blocks/{block_id}", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def patch_subflow_block(
    subflow_key: str,
    block_id: str,
    payload: BlockPatchInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="tenant_not_found")

    key = _slugify_key(subflow_key) or subflow_key
    vertical_key = getattr(tenant, "vertical_key", None)
    if not vertical_key:
        raise HTTPException(status_code=400, detail="tenant_missing_vertical")
    overrides_payload = load_subflow_overrides_payload(db, str(tenant.id))
    composition_mode = get_composition_mode(overrides_payload)
    if not overrides_payload.get("composition_mode"):
        composition_mode = vertical_subflow_composition_default(str(vertical_key)) or "router"

    subflow_file = None
    if composition_mode == "sequential":
        scope_key = _router_scope_for_tenant(tenant, None) or "default"
        subflow_file, _subflow_id = _resolve_sequential_subflow_file(
            vertical_key=str(vertical_key), scope_key=scope_key, key=key
        )
    else:
        flow, router_cfg, routes_payload = _flow_router_and_routes_for_tenant(db, tenant)
        if not flow:
            raise HTTPException(status_code=404, detail="router_not_configured")
        effective_router_cfg = router_cfg if isinstance(router_cfg, dict) else _infer_router_cfg_from_flow(flow)
        save_to = str((effective_router_cfg or {}).get("save_to") or "").strip().lower()
        if not save_to:
            raise HTTPException(status_code=404, detail="router_not_configured")
        scope_key = _router_scope_for_tenant(tenant, effective_router_cfg)
        subflow_file, _subflow_id = _resolve_subflow_file(
            vertical_key=str(vertical_key),
            scope_key=scope_key,
            save_to=save_to,
            key=key,
            routes_payload=routes_payload,
        )
    if not subflow_file:
        raise HTTPException(status_code=404, detail="subflow_not_found")

    base = vertical_read_asset_json(str(vertical_key), str(subflow_file))
    blocks = base.get("blocks") if isinstance(base, dict) else None
    if not isinstance(blocks, dict) or block_id not in blocks or not isinstance(blocks.get(block_id), dict):
        raise HTTPException(status_code=404, detail="block_not_found")
    if isinstance(base, dict) and not _subflow_enabled(base):
        raise HTTPException(status_code=404, detail="subflow_disabled")
    locks = vertical_subflow_locks(str(vertical_key))
    _required, locked = _subflow_lock_flags(locks, key)
    if locked:
        raise HTTPException(status_code=403, detail="subflow_locked")
    base_block = blocks[block_id]

    overrides_payload = overrides_payload if isinstance(overrides_payload, dict) else {}
    overrides = overrides_payload.get("overrides") if isinstance(overrides_payload.get("overrides"), dict) else {}
    overrides = overrides if isinstance(overrides, dict) else {}

    entry = overrides.get(str(subflow_file))
    entry = entry if isinstance(entry, dict) else {}
    entry_blocks = entry.get("blocks") if isinstance(entry.get("blocks"), dict) else {}

    patch_obj: dict[str, Any] = entry_blocks.get(block_id) if isinstance(entry_blocks.get(block_id), dict) else {}

    if payload.text is not None:
        patch_text = payload.text.model_dump(exclude_none=True)
        t = patch_obj.get("text") if isinstance(patch_obj.get("text"), dict) else {}
        for k2, v2 in patch_text.items():
            if v2 is not None:
                t[str(k2)] = str(v2)
        patch_obj["text"] = t

    if payload.text_enriched is not None:
        patch_text = payload.text_enriched.model_dump(exclude_none=True)
        t = patch_obj.get("text_enriched") if isinstance(patch_obj.get("text_enriched"), dict) else {}
        for k2, v2 in patch_text.items():
            if v2 is not None:
                t[str(k2)] = str(v2)
        patch_obj["text_enriched"] = t

    if payload.text_variants is not None:
        patch_obj["text_variants"] = [str(v) for v in payload.text_variants if v is not None]

    if payload.options is not None:
        if str(base_block.get("type") or "") not in {"buttons", "options"}:
            raise HTTPException(status_code=400, detail="block_not_options")
        has_branching = isinstance(base_block.get("next_map"), dict) or isinstance(base_block.get("branches"), dict)
        allow_add = (not has_branching) and bool(base_block.get("next"))

        base_opts = base_block.get("options") if isinstance(base_block.get("options"), list) else []
        base_ids: set[str] = set()
        for opt in base_opts:
            if not isinstance(opt, dict):
                continue
            oid = opt.get("id") if opt.get("id") is not None else opt.get("value")
            if oid is None:
                continue
            base_ids.add(str(oid))

        existing_patch_opts = patch_obj.get("options") if isinstance(patch_obj.get("options"), list) else []
        patch_by_id: dict[str, dict] = {}
        for opt in existing_patch_opts:
            if not isinstance(opt, dict):
                continue
            oid = opt.get("id")
            if oid is None:
                continue
            patch_by_id[str(oid)] = opt

        for opt_patch in payload.options:
            oid = str(opt_patch.id).strip()
            if not oid:
                continue
            if isinstance(opt_patch.label, TextPatch):
                label_val: Any = opt_patch.label.model_dump(exclude_none=True)
            else:
                label_val = str(opt_patch.label)

            if oid in patch_by_id:
                patch_by_id[oid]["label"] = label_val
                continue
            if oid in base_ids or allow_add:
                existing_patch_opts.append({"id": oid, "label": label_val})
                patch_by_id[oid] = existing_patch_opts[-1]
                continue
            raise HTTPException(status_code=400, detail="cannot_add_options_on_branching_block")

        patch_obj["options"] = existing_patch_opts

    entry_blocks[block_id] = patch_obj
    entry["blocks"] = entry_blocks
    overrides[str(subflow_file)] = entry
    overrides_payload["overrides"] = overrides

    cfg = save_subflow_overrides_payload(db, str(tenant.id), overrides_payload)
    return {
        "tenant_id": str(tenant.id),
        "config_id": str(cfg.id),
        "version": int(cfg.version),
        "file": str(subflow_file),
        "block_id": str(block_id),
    }
