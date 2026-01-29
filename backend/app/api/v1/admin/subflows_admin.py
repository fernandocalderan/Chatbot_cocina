from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import sqlalchemy as sa

from app.api.deps import get_db
from app.middleware.authz import require_role
from app.models.flows import Flow as FlowVersioned
from app.models.users import UserRole
from app.services.subflow_router import normalize_keywords, simulate_subflow_routing

router = APIRouter(
    prefix="/admin/subflows",
    tags=["admin"],
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN.value))],
)

SLUG_RE = re.compile(r"^[a-z0-9_\-]{2,}$")


class SubflowCreatePayload(BaseModel):
    vertical_key: str = Field(..., min_length=1)
    scope_key: str = Field(..., min_length=1)
    parent_flow_id: str = Field(..., min_length=1)
    subflow_key: str | None = None
    display_name: str = Field(..., min_length=1, max_length=255)
    content_text: str = Field(..., min_length=1)
    trigger_keywords: list[str] | None = None
    trigger_priority: int = 5
    trigger_threshold: int = 1
    owner_type: str = "GLOBAL"
    owner_id: str | None = None


class SubflowUpdatePayload(BaseModel):
    subflow_key: str | None = None
    trigger_keywords: list[str] | None = None
    trigger_priority: int | None = None
    trigger_threshold: int | None = None
    enabled: bool | None = None


class SubflowClonePayload(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    base_flow_id: str = Field(..., min_length=1)


def _slugify(value: str) -> str:
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


def _generate_subflow_schema(display_name: str, content_text: str) -> dict[str, Any]:
    intro = (content_text or "").strip() or f"Guia para {display_name}"
    return {
        "start_block": "welcome",
        "blocks": {
            "welcome": {
                "type": "message",
                "text": intro,
                "next": "ask_details",
            },
            "ask_details": {
                "type": "message",
                "text": "Quieres que profundicemos en este tema?",
                "next": "end",
            },
            "end": {
                "type": "message",
                "text": "Perfecto. Si necesitas algo mas, dime.",
                "end": True,
            },
        },
    }


def _validate_flow_schema(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="invalid_flow_schema")
    if not isinstance(data.get("blocks"), dict) or not data.get("blocks"):
        raise HTTPException(status_code=400, detail="missing_blocks")
    if not data.get("start_block"):
        raise HTTPException(status_code=400, detail="missing_start_block")


def _next_version_for_subflow(
    db: Session,
    *,
    owner_type: str,
    owner_id: str | None,
    vertical_key: str,
    scope_key: str,
    parent_flow_id: str,
    subflow_key: str,
) -> int:
    q = db.query(sa.func.max(FlowVersioned.version)).filter(
        FlowVersioned.owner_type == owner_type,
        FlowVersioned.flow_kind == "subflow",
        FlowVersioned.vertical_key == vertical_key,
        FlowVersioned.scope_key == scope_key,
        FlowVersioned.parent_flow_id == parent_flow_id,
        FlowVersioned.subflow_key == subflow_key,
    )
    if owner_id:
        q = q.filter(FlowVersioned.owner_id == owner_id)
    else:
        q = q.filter(FlowVersioned.owner_id.is_(None))
    current = q.scalar() or 0
    return int(current) + 1


def _ensure_owner(owner_type: str, owner_id: str | None) -> tuple[str, str | None, str | None]:
    owner_type_norm = str(owner_type or "GLOBAL").upper()
    if owner_type_norm not in {"GLOBAL", "TENANT"}:
        raise HTTPException(status_code=400, detail="invalid_owner_type")
    if owner_type_norm == "TENANT" and not owner_id:
        raise HTTPException(status_code=400, detail="missing_owner_id")
    tenant_id = owner_id if owner_type_norm == "TENANT" else None
    return owner_type_norm, owner_id if owner_type_norm == "TENANT" else None, tenant_id


def _ensure_unique_subflow_key(
    db: Session,
    *,
    owner_type: str,
    owner_id: str | None,
    parent_flow_id: str,
    subflow_key: str,
) -> None:
    q = db.query(FlowVersioned).filter(
        FlowVersioned.flow_kind == "subflow",
        FlowVersioned.owner_type == owner_type,
        FlowVersioned.parent_flow_id == parent_flow_id,
        FlowVersioned.subflow_key == subflow_key,
        FlowVersioned.archived.is_(False),
    )
    if owner_id:
        q = q.filter(FlowVersioned.owner_id == owner_id)
    else:
        q = q.filter(FlowVersioned.owner_id.is_(None))
    if q.first():
        raise HTTPException(status_code=409, detail="subflow_key_already_exists")


@router.post("/create")
def create_subflow(payload: SubflowCreatePayload, db: Session = Depends(get_db)):
    subflow_key = _slugify(payload.subflow_key or payload.display_name)
    if not subflow_key or not SLUG_RE.match(subflow_key):
        raise HTTPException(status_code=400, detail="invalid_subflow_key")

    owner_type, owner_id, tenant_id = _ensure_owner(payload.owner_type, payload.owner_id)
    _ensure_unique_subflow_key(
        db,
        owner_type=owner_type,
        owner_id=owner_id,
        parent_flow_id=str(payload.parent_flow_id),
        subflow_key=subflow_key,
    )

    schema = _generate_subflow_schema(payload.display_name, payload.content_text)
    _validate_flow_schema(schema)

    keywords = normalize_keywords(payload.trigger_keywords)
    version = _next_version_for_subflow(
        db,
        owner_type=owner_type,
        owner_id=owner_id,
        vertical_key=payload.vertical_key,
        scope_key=payload.scope_key,
        parent_flow_id=str(payload.parent_flow_id),
        subflow_key=subflow_key,
    )

    new_flow = FlowVersioned(
        tenant_id=tenant_id,
        vertical_key=str(payload.vertical_key),
        scope_key=str(payload.scope_key),
        version=version,
        schema_json=schema,
        estado="draft",
        published_at=None,
        owner_type=owner_type,
        owner_id=owner_id,
        flow_kind="subflow",
        parent_flow_id=str(payload.parent_flow_id),
        subflow_key=subflow_key,
        trigger_keywords=keywords,
        trigger_priority=int(payload.trigger_priority or 5),
        trigger_threshold=int(payload.trigger_threshold or 1),
        archived=False,
        enabled=True,
    )
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    return {"flow_id": str(new_flow.id), "version": new_flow.version, "status": "draft"}


@router.post("/import")
def import_subflow(
    file: UploadFile = File(...),
    vertical_key: str = Form(...),
    scope_key: str = Form(...),
    parent_flow_id: str = Form(...),
    subflow_key: str = Form(...),
    trigger_keywords: str | None = Form(None),
    trigger_priority: int = Form(5),
    trigger_threshold: int = Form(1),
    owner_type: str = Form("GLOBAL"),
    owner_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    try:
        raw = file.file.read()
        content = raw.decode("utf-8")
        data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_json")

    _validate_flow_schema(data)

    owner_type_norm, owner_id_norm, tenant_id = _ensure_owner(owner_type, owner_id)

    subflow_key_norm = _slugify(subflow_key)
    if not subflow_key_norm or not SLUG_RE.match(subflow_key_norm):
        raise HTTPException(status_code=400, detail="invalid_subflow_key")

    _ensure_unique_subflow_key(
        db,
        owner_type=owner_type_norm,
        owner_id=owner_id_norm,
        parent_flow_id=str(parent_flow_id),
        subflow_key=subflow_key_norm,
    )

    kw_list: list[str] | None = None
    if trigger_keywords:
        trigger_keywords = trigger_keywords.strip()
        if trigger_keywords.startswith("["):
            try:
                kw_list = json.loads(trigger_keywords)
            except Exception:
                kw_list = None
        if kw_list is None:
            kw_list = [k.strip() for k in trigger_keywords.split(",") if k.strip()]
    keywords = normalize_keywords(kw_list)

    version = _next_version_for_subflow(
        db,
        owner_type=owner_type_norm,
        owner_id=owner_id_norm,
        vertical_key=vertical_key,
        scope_key=scope_key,
        parent_flow_id=str(parent_flow_id),
        subflow_key=subflow_key_norm,
    )

    new_flow = FlowVersioned(
        tenant_id=tenant_id,
        vertical_key=str(vertical_key),
        scope_key=str(scope_key),
        version=version,
        schema_json=data,
        estado="draft",
        published_at=None,
        owner_type=owner_type_norm,
        owner_id=owner_id_norm,
        flow_kind="subflow",
        parent_flow_id=str(parent_flow_id),
        subflow_key=subflow_key_norm,
        trigger_keywords=keywords,
        trigger_priority=int(trigger_priority or 5),
        trigger_threshold=int(trigger_threshold or 1),
        archived=False,
        enabled=True,
    )
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)
    return {"flow_id": str(new_flow.id), "version": new_flow.version, "status": "draft"}


@router.post("/{flow_id}/publish")
def publish_subflow(flow_id: str, db: Session = Depends(get_db)):
    flow = db.query(FlowVersioned).filter(FlowVersioned.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="flow_not_found")
    if str(getattr(flow, "flow_kind", "")) != "subflow":
        raise HTTPException(status_code=400, detail="invalid_flow_kind")

    owner_type = str(getattr(flow, "owner_type", "") or "GLOBAL").upper()
    owner_id = getattr(flow, "owner_id", None)
    q = db.query(FlowVersioned).filter(
        FlowVersioned.owner_type == owner_type,
        FlowVersioned.flow_kind == "subflow",
        FlowVersioned.parent_flow_id == flow.parent_flow_id,
        FlowVersioned.subflow_key == flow.subflow_key,
        FlowVersioned.archived.is_(False),
    )
    if owner_id:
        q = q.filter(FlowVersioned.owner_id == owner_id)
    else:
        q = q.filter(FlowVersioned.owner_id.is_(None))
    if flow.vertical_key:
        q = q.filter(FlowVersioned.vertical_key == flow.vertical_key)
    if flow.scope_key:
        q = q.filter(FlowVersioned.scope_key == flow.scope_key)

    q.update({"estado": "draft", "published_at": None})

    flow.estado = "published"
    flow.published_at = datetime.now(timezone.utc)
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return {
        "flow_id": str(flow.id),
        "published": True,
        "published_at": flow.published_at.isoformat() if flow.published_at else None,
        "version": flow.version,
    }


@router.post("/{flow_id}/archive")
def archive_subflow(flow_id: str, db: Session = Depends(get_db)):
    flow = db.query(FlowVersioned).filter(FlowVersioned.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="flow_not_found")
    flow.archived = True
    flow.estado = "draft"
    flow.published_at = None
    db.add(flow)
    db.commit()
    db.refresh(flow)
    return {"flow_id": str(flow.id), "archived": True}


@router.patch("/{flow_id}")
def update_subflow(flow_id: str, payload: SubflowUpdatePayload, db: Session = Depends(get_db)):
    flow = db.query(FlowVersioned).filter(FlowVersioned.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="flow_not_found")
    if str(getattr(flow, "flow_kind", "")) != "subflow":
        raise HTTPException(status_code=400, detail="invalid_flow_kind")

    if payload.subflow_key:
        subflow_key_norm = _slugify(payload.subflow_key)
        if not subflow_key_norm or not SLUG_RE.match(subflow_key_norm):
            raise HTTPException(status_code=400, detail="invalid_subflow_key")
        if subflow_key_norm != getattr(flow, "subflow_key", None):
            _ensure_unique_subflow_key(
                db,
                owner_type=str(getattr(flow, "owner_type", "") or "GLOBAL").upper(),
                owner_id=getattr(flow, "owner_id", None),
                parent_flow_id=str(getattr(flow, "parent_flow_id")),
                subflow_key=subflow_key_norm,
            )
            flow.subflow_key = subflow_key_norm

    if payload.trigger_keywords is not None:
        flow.trigger_keywords = normalize_keywords(payload.trigger_keywords)
    if payload.trigger_priority is not None:
        flow.trigger_priority = int(payload.trigger_priority)
    if payload.trigger_threshold is not None:
        flow.trigger_threshold = int(payload.trigger_threshold)
    if payload.enabled is not None:
        flow.enabled = bool(payload.enabled)

    db.add(flow)
    db.commit()
    db.refresh(flow)
    return {
        "flow_id": str(flow.id),
        "subflow_key": flow.subflow_key,
        "trigger_keywords": flow.trigger_keywords,
        "trigger_priority": flow.trigger_priority,
        "trigger_threshold": flow.trigger_threshold,
        "enabled": bool(getattr(flow, "enabled", True)),
    }


@router.post("/{flow_id}/update")
def update_subflow_legacy(flow_id: str, payload: SubflowUpdatePayload, db: Session = Depends(get_db)):
    return update_subflow(flow_id=flow_id, payload=payload, db=db)


@router.get("/simulate")
def simulate_subflows(
    tenant_id: str,
    base_flow_id: str,
    text: str,
    db: Session = Depends(get_db),
):
    result = simulate_subflow_routing(
        db=db,
        tenant_id=str(tenant_id),
        base_flow_id=str(base_flow_id),
        user_text=str(text or ""),
    )
    return result


@router.post("/clone-to-tenant")
def clone_subflows_to_tenant(payload: SubflowClonePayload, db: Session = Depends(get_db)):
    tenant_id = str(payload.tenant_id)
    base_flow_id = str(payload.base_flow_id)
    global_flows = (
        db.query(FlowVersioned)
        .filter(
            FlowVersioned.flow_kind == "subflow",
            FlowVersioned.parent_flow_id == base_flow_id,
            FlowVersioned.owner_type == "GLOBAL",
            FlowVersioned.owner_id.is_(None),
            FlowVersioned.archived.is_(False),
        )
        .all()
    )
    created = []
    skipped = []
    for flow in global_flows:
        exists = (
            db.query(FlowVersioned)
            .filter(
                FlowVersioned.flow_kind == "subflow",
                FlowVersioned.parent_flow_id == base_flow_id,
                FlowVersioned.owner_type == "TENANT",
                FlowVersioned.owner_id == tenant_id,
                FlowVersioned.subflow_key == flow.subflow_key,
                FlowVersioned.archived.is_(False),
            )
            .first()
        )
        if exists:
            skipped.append(str(flow.subflow_key))
            continue
        version = _next_version_for_subflow(
            db,
            owner_type="TENANT",
            owner_id=tenant_id,
            vertical_key=str(flow.vertical_key or ""),
            scope_key=str(flow.scope_key or ""),
            parent_flow_id=base_flow_id,
            subflow_key=str(flow.subflow_key or ""),
        )
        clone = FlowVersioned(
            tenant_id=tenant_id,
            vertical_key=flow.vertical_key,
            scope_key=flow.scope_key,
            version=version,
            schema_json=flow.schema_json,
            estado="draft",
            published_at=None,
            owner_type="TENANT",
            owner_id=tenant_id,
            flow_kind="subflow",
            parent_flow_id=base_flow_id,
            subflow_key=flow.subflow_key,
            trigger_keywords=flow.trigger_keywords,
            trigger_priority=flow.trigger_priority,
            trigger_threshold=flow.trigger_threshold,
            archived=False,
            enabled=bool(getattr(flow, "enabled", True)),
        )
        db.add(clone)
        db.commit()
        db.refresh(clone)
        created.append(str(clone.id))

    return {"created": created, "skipped": skipped}
