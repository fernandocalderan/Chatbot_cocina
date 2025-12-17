from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import oauth2_scheme
from app.api.deps import get_db, get_tenant_id
from app.middleware.authz import require_any_role
from app.models.configs import Config
from app.models.tenants import Tenant
from app.services.flow_templates import list_flow_templates
from app.services.verticals import list_flow_templates_for_vertical, allowed_flow_ids


router = APIRouter(prefix="/tenant/automation", tags=["tenant-automation"])

CONFIG_TIPO_MATERIALS = "tenant_flow_materials"
CONFIG_TIPO_WIDGET = "tenant_widget_config"


def _safe_int(value, default: int) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _normalize_visual(payload: dict) -> dict:
    visual = payload.get("visual") if isinstance(payload.get("visual"), dict) else {}
    return {
        "primary_color": visual.get("primary_color") or "#6B5B95",
        "secondary_color": visual.get("secondary_color") or "#EDE9FE",
        "accent_color": visual.get("accent_color") or "#C9A24D",
        "logo_url": visual.get("logo_url"),
        "position": visual.get("position") or "bottom-right",
        "size": visual.get("size") or "md",
        "tone": visual.get("tone") or "serio",
        "font_family": visual.get("font_family") or "Inter",
        "font_size": _safe_int(visual.get("font_size"), 14),
        "border_radius": _safe_int(visual.get("border_radius"), 16),
    }


def _normalize_materials(payload: dict) -> dict:
    content = payload.get("content") if isinstance(payload.get("content"), dict) else {}
    automation = payload.get("automation") if isinstance(payload.get("automation"), dict) else {}
    return {
        "flow_id": payload.get("flow_id"),
        "content": {
            "welcome": content.get("welcome") or "",
            "questions": content.get("questions") or {},
            "buttons": content.get("buttons") or {},
            "errors": content.get("errors") or {},
            "closing": content.get("closing") or "",
            "language": content.get("language") or "es",
            "tone": content.get("tone") or "serio",
        },
        "automation": {
            "ai_level": automation.get("ai_level") or "medium",
            "saving_mode": bool(automation.get("saving_mode") or False),
            "human_fallback": bool(automation.get("human_fallback") if "human_fallback" in automation else True),
            "max_response_seconds": automation.get("max_response_seconds") or 8,
            "ai_steps": automation.get("ai_steps") or [],
        },
    }


def _load_latest_materials(db: Session, tenant_id: str, status_filter: str | None = None) -> dict | None:
    rows = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .all()
    )
    for row in rows:
        payload = row.payload_json or {}
        status_val = str(payload.get("status") or "").upper()
        if status_filter and status_val != status_filter:
            continue
        payload["version"] = row.version
        payload["updated_at"] = row.updated_at.isoformat() if row.updated_at else None
        return payload
    return None


def _load_all_published(db: Session, tenant_id: str) -> list[dict]:
    rows = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .all()
    )
    items: list[dict] = []
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() != "PUBLISHED":
            continue
        items.append(
            {
                "version": row.version,
                "flow_id": payload.get("flow_id"),
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
        )
    return items


def _next_version(db: Session, tenant_id: str) -> int:
    row = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
        .order_by(Config.version.desc())
        .first()
    )
    return (row.version + 1) if row else 1


def _load_widget_visual(db: Session, tenant_id: str, tenant: Tenant | None) -> dict:
    row = (
        db.query(Config)
        .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_WIDGET)
        .order_by(Config.version.desc(), Config.updated_at.desc())
        .first()
    )
    if row and isinstance(row.payload_json, dict) and isinstance(row.payload_json.get("visual"), dict):
        visual = row.payload_json.get("visual") or {}
    else:
        branding = getattr(tenant, "branding", {}) or {}
        visual = (branding.get("widget") or {}).get("visual") if isinstance(branding.get("widget"), dict) else {}
    return _normalize_visual({"visual": visual})


class MaterialsDraftInput(BaseModel):
    flow_id: str | None = None
    content: dict[str, Any] | None = None
    automation: dict[str, Any] | None = None
    visual: dict[str, Any] | None = None


@router.get("/materials", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def get_materials(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    draft = _load_latest_materials(db, tenant_id, status_filter="DRAFT")
    published = _load_latest_materials(db, tenant_id, status_filter="PUBLISHED")
    visual = _load_widget_visual(db, tenant_id, tenant)
    return {
        "draft": draft,
        "published": published,
        "visual": visual,
        "versions": _load_all_published(db, tenant_id),
        "available_flows": list_flow_templates_for_vertical(getattr(tenant, "vertical_key", None)),
    }


@router.put("/materials", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def save_materials_draft(
    payload: MaterialsDraftInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")

    if payload.flow_id:
        available_ids = set(allowed_flow_ids(getattr(tenant, "vertical_key", None)))
        if not available_ids:
            available_ids = {f.get("id") for f in list_flow_templates() if isinstance(f, dict)}
        if payload.flow_id not in available_ids:
            raise HTTPException(status_code=400, detail="invalid_flow_id")

    visual = _normalize_visual({"visual": payload.visual or {}})
    if visual:
        widget_row = (
            db.query(Config)
            .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_WIDGET)
            .order_by(Config.version.desc(), Config.updated_at.desc())
            .first()
        )
        next_ver = (widget_row.version + 1) if widget_row else 1
        widget_payload = {"visual": visual, "updated_at": datetime.now(timezone.utc).isoformat()}
        if widget_row:
            widget_row.version = next_ver
            widget_row.payload_json = widget_payload
            db.add(widget_row)
        else:
            db.add(
                Config(
                    tenant_id=tenant_id,
                    tipo=CONFIG_TIPO_WIDGET,
                    version=next_ver,
                    payload_json=widget_payload,
                )
            )

    current_draft = _load_latest_materials(db, tenant_id, status_filter="DRAFT")
    next_ver = current_draft.get("version") if current_draft else _next_version(db, tenant_id)
    normalized = _normalize_materials(payload.model_dump())
    normalized["status"] = "DRAFT"
    normalized["updated_at"] = datetime.now(timezone.utc).isoformat()

    if current_draft:
        draft_row = (
            db.query(Config)
            .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS, Config.version == next_ver)
            .order_by(Config.updated_at.desc())
            .first()
        )
        if draft_row:
            draft_row.payload_json = normalized
            db.add(draft_row)
        else:
            db.add(
                Config(
                    tenant_id=tenant_id,
                    tipo=CONFIG_TIPO_MATERIALS,
                    version=next_ver,
                    payload_json=normalized,
                )
            )
    else:
        db.add(
            Config(
                tenant_id=tenant_id,
                tipo=CONFIG_TIPO_MATERIALS,
                version=next_ver,
                payload_json=normalized,
            )
        )

    db.commit()
    return {"status": "ok", "version": next_ver}


@router.post("/materials/publish", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def publish_materials(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    draft = _load_latest_materials(db, tenant_id, status_filter="DRAFT")
    if not draft:
        raise HTTPException(status_code=400, detail="draft_not_found")
    next_ver = _next_version(db, tenant_id)
    payload = dict(draft)
    payload["status"] = "PUBLISHED"
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload.pop("version", None)
    payload.pop("updated_at", None)
    db.add(
        Config(
            tenant_id=tenant_id,
            tipo=CONFIG_TIPO_MATERIALS,
            version=next_ver,
            payload_json=payload,
        )
    )
    db.commit()
    return {"status": "ok", "version": next_ver}


class RollbackInput(BaseModel):
    version: int = Field(..., ge=1)


@router.post("/materials/rollback", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def rollback_materials(
    payload: RollbackInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    target = (
        db.query(Config)
        .filter(
            Config.tenant_id == tenant_id,
            Config.tipo == CONFIG_TIPO_MATERIALS,
            Config.version == payload.version,
        )
        .first()
    )
    if not target:
        raise HTTPException(status_code=404, detail="version_not_found")
    data = target.payload_json or {}
    if str(data.get("status") or "").upper() != "PUBLISHED":
        raise HTTPException(status_code=400, detail="version_not_published")
    next_ver = _next_version(db, tenant_id)
    data = dict(data)
    data["status"] = "PUBLISHED"
    data["rollback_from"] = payload.version
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    db.add(
        Config(
            tenant_id=tenant_id,
            tipo=CONFIG_TIPO_MATERIALS,
            version=next_ver,
            payload_json=data,
        )
    )
    db.commit()
    return {"status": "ok", "version": next_ver}
