import datetime
import secrets
import hashlib
from typing import Any, Optional

import jwt
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
import sqlalchemy as sa

from app.api.deps import get_db
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.middleware.authz import require_role
from app.models.ia_usage import IAUsage
from app.models.configs import Config
from app.models.flows import Flow as FlowVersioned
from app.models.leads import Lead
from app.models.tenants import Tenant, UsageMode
from app.models.users import UserRole, User
from app.models.login_tokens import LoginToken
from app.services.key_manager import KeyManager
from app.services.oidc_admin import validate_admin_id_token, OIDCValidationError
from app.services.template_service import TemplateService
from app.services.verticals import (
    list_verticals,
    get_vertical_config,
    provision_vertical_assets,
    get_vertical_bundle,
    resolve_flow_id,
    allowed_scopes,
    validate_vertical_scopes,
    vertical_flow_base,
)
from app.services.audit_service import AuditService
from app.services.email_service import send_magic_link
from app.services.flow_resolver import resolve_runtime_flow
from app.services.flow_templates import apply_materials
from app.core.logger import LOG_DIR

router = APIRouter(prefix="/admin", tags=["admin"])


def _ensure_super_admin():
    return require_role(UserRole.SUPER_ADMIN.value)


def _resolve_actor(auth_header: str | None, x_api_key: str | None) -> str:
    settings = get_settings()
    if x_api_key and settings.admin_api_token and x_api_key == settings.admin_api_token:
        return "admin_api_key"
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return "super_admin"
    token = auth_header.split(" ", 1)[1].strip()
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid") or "current"
    except Exception:
        return "super_admin"
    km = KeyManager()
    current_kid, current_secret, previous = km.get_jwt_keys()
    secrets_map = {current_kid: current_secret}
    secrets_map.update(previous)
    secret = secrets_map.get(kid)
    if not secret:
        return "super_admin"
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
        return payload.get("email") or payload.get("sub") or "super_admin"
    except Exception:
        return "super_admin"


def _next_customer_code(db) -> str:
    last = db.query(Tenant).order_by(Tenant.customer_code.desc()).first()
    seq = 0
    if last and getattr(last, "customer_code", None):
        try:
            seq = int(str(last.customer_code).split("-")[-1])
        except Exception:
            seq = 0
    seq += 1
    return f"OPN-{seq:06d}"


def _issue_magic_login_token(user: User, tenant: Tenant, db):
    settings = get_settings()
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    jti = jwt.utils.base64url_encode(secrets.token_bytes(16)).decode()
    token = jwt.encode(
        {
            "scope": "tenant_magic_login",
            "user_id": str(user.id),
            "tenant_id": str(tenant.id),
            "type": "TENANT",
            "roles": [user.role],
            "exp": exp,
            "jti": jti,
        },
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    login_token = LoginToken(
        user_id=user.id,
        token_hash=token_hash,
        jti=jti,
        expires_at=exp,
    )
    db.add(login_token)
    try:
        db.commit()
    except Exception:
        db.rollback()
    return token, exp


def _send_magic_link_email(email: str, token: str, expires_at: datetime.datetime):
    settings = get_settings()
    base = settings.panel_url or "https://panel.opunnence.com"
    link = f"{base.rstrip('/')}/magic-login?token={token}"
    try:
        send_magic_link(email, link)
    except Exception:
        pass


class AdminOIDCInput(BaseModel):
    id_token: str


class TenantBase(BaseModel):
    name: str
    contact_email: Optional[str] = None
    plan: str = "BASE"
    ia_monthly_limit_eur: Optional[float] = None
    usage_limit_monthly: Optional[float] = None
    allowed_origins: list[str] = Field(default_factory=list)
    maintenance: bool = False
    ia_enabled: Optional[bool] = None
    vertical_key: Optional[str] = None
    vertical_scopes: list[str] = Field(default_factory=list)


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    plan: Optional[str] = None
    ia_monthly_limit_eur: Optional[float] = None
    usage_limit_monthly: Optional[float] = None
    allowed_origins: Optional[list[str]] = None
    maintenance: Optional[bool] = None
    ia_enabled: Optional[bool] = None
    billing_status: Optional[str] = None
    vertical_key: Optional[str] = None
    vertical_scopes: Optional[list[str]] = None
    force_vertical: Optional[bool] = None


class WidgetTokenRequest(BaseModel):
    allowed_origin: str
    ttl_minutes: int = 30


class TenantExclude(BaseModel):
    reason: Optional[str] = None


class MagicLinkRequest(BaseModel):
    email: Optional[str] = None


CONFIG_TIPO_MATERIALS = "tenant_flow_materials"


def _load_published_materials(db, tenant_id: str) -> dict | None:
    try:
        rows = (
            db.query(Config)
            .filter(Config.tenant_id == tenant_id, Config.tipo == CONFIG_TIPO_MATERIALS)
            .order_by(Config.version.desc(), Config.updated_at.desc())
            .all()
        )
    except Exception:
        return None
    for row in rows:
        payload = row.payload_json or {}
        if str(payload.get("status") or "").upper() == "PUBLISHED":
            return payload if isinstance(payload, dict) else None
    return None


def _serialize_tenant(t: Tenant) -> dict[str, Any]:
    branding = getattr(t, "branding", {}) or {}
    return {
        "id": str(t.id),
        "customer_code": getattr(t, "customer_code", None),
        "name": t.name,
        "contact_email": t.contact_email,
        "plan": t.plan,
        "billing_status": getattr(t, "billing_status", None),
        "plan_changed_at": branding.get("plan_changed_at"),
        "ia_monthly_limit_eur": float(t.ia_monthly_limit_eur or 0),
        "allowed_origins": branding.get("allowed_widget_origins")
        or branding.get("allowed_origins")
        or [],
        "maintenance": bool(
            branding.get("maintenance_mode")
            or branding.get("maintenance")
            or False
        ),
        "use_ia": bool(getattr(t, "use_ia", False)),
        "ia_enabled": bool(getattr(t, "ia_enabled", True)),
        "usage_mode": getattr(t, "usage_mode", None),
        "usage_monthly": float(getattr(t, "usage_monthly", 0) or 0),
        "usage_limit_monthly": float(getattr(t, "usage_limit_monthly", 0) or 0)
        if getattr(t, "usage_limit_monthly", None) is not None
        else None,
        "needs_upgrade_notice": bool(getattr(t, "needs_upgrade_notice", False)),
        "default_template_id": str(getattr(t, "default_template_id")) if getattr(t, "default_template_id", None) else None,
        "widget_tokens_revoked_before": branding.get("widget_tokens_revoked_before"),
        "excluded": bool(branding.get("excluded", False)),
        "vertical_key": getattr(t, "vertical_key", None),
        "vertical_scopes": branding.get("vertical_scopes") or [],
    }


@router.get("/tenants", dependencies=[Depends(_ensure_super_admin())])
def list_tenants(search: Optional[str] = Query(None, max_length=100), db=Depends(get_db)):
    q = db.query(Tenant)
    if search:
        term = f"%{search.strip().lower()}%"
        q = q.filter(
            sa.or_(
                sa.func.lower(Tenant.name).ilike(term),
                sa.func.lower(Tenant.contact_email).ilike(term),
                sa.func.lower(Tenant.customer_code).ilike(term),
            )
        )
    tenants = q.all()
    return [_serialize_tenant(t) for t in tenants]


@router.get("/verticals", dependencies=[Depends(_ensure_super_admin())])
def list_verticals_admin():
    return {"items": list_verticals()}


@router.get("/verticals/{vertical_key}", dependencies=[Depends(_ensure_super_admin())])
def get_vertical_admin(vertical_key: str):
    data = get_vertical_bundle(vertical_key)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vertical_not_found")
    return data


@router.post("/auth/login")
def admin_oidc_login(payload: AdminOIDCInput):
    settings = get_settings()
    try:
        claims = validate_admin_id_token(payload.id_token)
    except OIDCValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60)
    token = jwt.encode(
        {
            "type": "ADMIN",
            "roles": [UserRole.SUPER_ADMIN.value],
            "email": claims.get("email"),
            "exp": exp,
            "jti": jwt.utils.base64url_encode(secrets.token_bytes(16)).decode(),
        },
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    return {"token": token, "expires_at": exp.isoformat() + "Z", "email": claims.get("email")}


@router.post("/tenants", dependencies=[Depends(_ensure_super_admin())])
def create_tenant(payload: TenantCreate, request: Request, db=Depends(get_db)):
    if not payload.vertical_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_vertical_key")
    if not get_vertical_config(payload.vertical_key):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_vertical_key")
    try:
        scopes = validate_vertical_scopes(payload.vertical_key, payload.vertical_scopes)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_vertical_scopes")
    if allowed_scopes(payload.vertical_key) and not scopes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_vertical_scopes")
    branding = {
        "allowed_widget_origins": payload.allowed_origins or [],
        "maintenance": payload.maintenance,
        "vertical_scopes": scopes,
    }
    customer_code = _next_customer_code(db)
    tenant = Tenant(
        customer_code=customer_code,
        name=payload.name,
        contact_email=payload.contact_email,
        plan=payload.plan,
        ia_monthly_limit_eur=payload.ia_monthly_limit_eur,
        usage_limit_monthly=payload.usage_limit_monthly,
        branding=branding,
        ia_enabled=payload.ia_enabled if payload.ia_enabled is not None else True,
        vertical_key=payload.vertical_key,
        flow_mode="VERTICAL",
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    try:
        cloned_tpl = TemplateService.clone_default_template(db, str(tenant.id))
        if cloned_tpl:
            tenant.default_template_id = cloned_tpl.id
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
    except Exception:
        db.rollback()
    try:
        created = provision_vertical_assets(db, tenant)
    except Exception:
        db.rollback()
        created = None
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.create",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"plan": tenant.plan, "vertical_key": tenant.vertical_key},
    )
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.customer_code_assigned",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"customer_code": customer_code},
    )
    AuditService.log_admin_action(
        actor=actor,
        action="tenant_created_with_vertical",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"vertical_key": tenant.vertical_key, "provisioned": created or {}},
    )
    if tenant.contact_email:
        owner = User(
            tenant_id=tenant.id,
            email=tenant.contact_email,
            role=UserRole.OWNER.value,
            hashed_password=None,
            must_set_password=True,
            status="ACTIVE",
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)
        magic_token, exp = _issue_magic_login_token(owner, tenant, db)
        _send_magic_link_email(tenant.contact_email, magic_token, exp)
    return _serialize_tenant(tenant)


@router.patch("/tenants/{tenant_id}", dependencies=[Depends(_ensure_super_admin())])
def update_tenant(tenant_id: str, payload: TenantUpdate, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    previous_plan = tenant.plan
    if payload.allowed_origins is not None:
        branding["allowed_widget_origins"] = payload.allowed_origins
    if payload.maintenance is not None:
        branding["maintenance"] = bool(payload.maintenance)
        branding["maintenance_mode"] = bool(payload.maintenance)
    updates = payload.model_dump(
        exclude_none=True,
        exclude={"allowed_origins", "maintenance", "force_vertical", "vertical_scopes"},
    )

    # Sub-vertical scopes (branding) – inmutables salvo `force_vertical`
    if payload.vertical_scopes is not None:
        current_vertical = updates.get("vertical_key") or getattr(tenant, "vertical_key", None)
        if not current_vertical:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_vertical_key")
        try:
            scopes = validate_vertical_scopes(current_vertical, payload.vertical_scopes)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_vertical_scopes")
        existing_scopes = branding.get("vertical_scopes") or []
        if existing_scopes and scopes != existing_scopes and not payload.force_vertical:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="vertical_scopes_immutable")
        branding["vertical_scopes"] = scopes
    if "vertical_key" in updates:
        if not get_vertical_config(updates["vertical_key"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_vertical_key")
        if tenant.vertical_key and updates["vertical_key"] != tenant.vertical_key and not payload.force_vertical:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="vertical_key_immutable")
        tenant.vertical_key = updates.pop("vertical_key")
        if payload.force_vertical:
            existing_scopes = branding.get("vertical_scopes") or []
            if allowed_scopes(tenant.vertical_key) and not existing_scopes:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_vertical_scopes")
        try:
            created = provision_vertical_assets(db, tenant)
        except Exception:
            db.rollback()
            created = None
        if payload.force_vertical:
            actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
            AuditService.log_admin_action(
                actor=actor,
                action="tenant_vertical_override_manual_admin",
                entity="tenant",
                entity_id=str(tenant.id),
                tenant_id=str(tenant.id),
                meta={"vertical_key": tenant.vertical_key, "provisioned": created or {}},
            )
    for field, value in updates.items():
        setattr(tenant, field, value)
    if payload.plan and payload.plan != previous_plan:
        branding["plan_changed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.update",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta=payload.model_dump(exclude_none=True),
    )
    return _serialize_tenant(tenant)


@router.get("/tenants/{tenant_id}/flow", dependencies=[Depends(_ensure_super_admin())])
def get_tenant_flow(tenant_id: str, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")

    materials = _load_published_materials(db, str(tenant.id))
    flow_id_override = materials.get("flow_id") if isinstance(materials, dict) else None
    flow_id_override = resolve_flow_id(flow_id_override, getattr(tenant, "vertical_key", None))

    plan_value = getattr(tenant, "plan", "base")
    if hasattr(plan_value, "value"):
        plan_value = plan_value.value

    flow_data = resolve_runtime_flow(
        db=db,
        tenant=tenant,
        flow_id_override=flow_id_override,
        plan_value=str(plan_value or "base").lower(),
    )
    flow_data = apply_materials(flow_data, materials)

    published = None
    try:
        row = (
            db.query(FlowVersioned)
            .filter(FlowVersioned.tenant_id == tenant.id, FlowVersioned.estado == "published")
            .order_by(FlowVersioned.published_at.desc().nullslast(), FlowVersioned.version.desc())
            .first()
        )
        if row:
            published = {
                "flow_id": str(row.id),
                "version": row.version,
                "published_at": row.published_at.isoformat() if row.published_at else None,
                "vertical_key": getattr(row, "vertical_key", None),
            }
    except Exception:
        published = None

    return {
        "tenant_id": str(tenant.id),
        "vertical_key": getattr(tenant, "vertical_key", None),
        "flow_mode": getattr(tenant, "flow_mode", None),
        "active_flow_id": str(getattr(tenant, "active_flow_id")) if getattr(tenant, "active_flow_id", None) else None,
        "published": published,
        "flow": flow_data if isinstance(flow_data, dict) else {},
    }


@router.post("/tenants/{tenant_id}/flow", dependencies=[Depends(_ensure_super_admin())])
def publish_tenant_flow(tenant_id: str, payload: dict, request: Request, db=Depends(get_db)):
    if not isinstance(payload, dict) or not payload:
        raise HTTPException(status_code=400, detail="invalid_payload")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")

    latest = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1
    now = datetime.datetime.now(datetime.timezone.utc)
    new_flow = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(getattr(tenant, "vertical_key", "") or "") or None,
        version=next_version,
        schema_json=payload,
        estado="published",
        published_at=now,
    )
    db.add(new_flow)
    db.flush()
    try:
        tenant.active_flow_id = new_flow.id
        tenant.flow_mode = "VERTICAL"
        db.add(tenant)
    except Exception:
        pass
    db.commit()
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.flow.publish",
        entity="flow",
        entity_id=str(new_flow.id),
        tenant_id=str(tenant.id),
        meta={"version": new_flow.version, "vertical_key": getattr(tenant, "vertical_key", None)},
    )
    return {
        "tenant_id": str(tenant.id),
        "flow_id": str(new_flow.id),
        "version": new_flow.version,
        "estado": new_flow.estado,
        "published_at": new_flow.published_at.isoformat() if new_flow.published_at else None,
    }


@router.post("/tenants/{tenant_id}/flow/reset", dependencies=[Depends(_ensure_super_admin())])
def reset_tenant_flow_to_vertical_base(tenant_id: str, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    if not getattr(tenant, "vertical_key", None):
        raise HTTPException(status_code=400, detail="missing_vertical_key")

    branding = getattr(tenant, "branding", {}) or {}
    base = vertical_flow_base(getattr(tenant, "vertical_key", None), branding.get("vertical_scopes") or [])
    if not isinstance(base, dict) or not base:
        raise HTTPException(status_code=400, detail="vertical_flow_base_not_found")

    try:
        provision_vertical_assets(db, tenant)
    except Exception:
        db.rollback()

    latest = (
        db.query(FlowVersioned)
        .filter(FlowVersioned.tenant_id == tenant.id)
        .order_by(FlowVersioned.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1
    now = datetime.datetime.now(datetime.timezone.utc)
    new_flow = FlowVersioned(
        tenant_id=tenant.id,
        vertical_key=str(getattr(tenant, "vertical_key", "") or "") or None,
        version=next_version,
        schema_json=base,
        estado="published",
        published_at=now,
    )
    db.add(new_flow)
    db.flush()
    try:
        tenant.active_flow_id = new_flow.id
        tenant.flow_mode = "VERTICAL"
        db.add(tenant)
    except Exception:
        pass
    db.commit()
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.flow.reset_to_vertical_base",
        entity="flow",
        entity_id=str(new_flow.id),
        tenant_id=str(tenant.id),
        meta={"version": new_flow.version, "vertical_key": getattr(tenant, "vertical_key", None)},
    )
    return {
        "tenant_id": str(tenant.id),
        "flow_id": str(new_flow.id),
        "version": new_flow.version,
        "estado": new_flow.estado,
        "published_at": new_flow.published_at.isoformat() if new_flow.published_at else None,
    }


@router.post("/tenants/{tenant_id}/maintenance", dependencies=[Depends(_ensure_super_admin())])
def toggle_maintenance(tenant_id: str, maintenance: bool, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    branding["maintenance"] = bool(maintenance)
    branding["maintenance_mode"] = bool(maintenance)
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.maintenance",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"maintenance": bool(maintenance)},
    )
    return {"tenant_id": str(tenant.id), "maintenance": bool(maintenance)}


@router.post("/tenants/{tenant_id}/widget-token", dependencies=[Depends(_ensure_super_admin())])
def issue_widget_token_admin(tenant_id: str, payload: WidgetTokenRequest, request: Request, db=Depends(get_db)):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="jwt_secret_not_configured",
        )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    allowed = branding.get("allowed_widget_origins") or branding.get("allowed_origins") or []
    if allowed and payload.allowed_origin not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="origin_not_allowed"
        )
    ttl = min(max(payload.ttl_minutes, 15), 60)
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ttl)
    issued_at = datetime.datetime.now(datetime.timezone.utc)
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    signed = jwt.encode(
        {
            "type": "WIDGET",
            "tenant_id": tenant_id,
            "allowed_origin": payload.allowed_origin,
            "exp": exp,
            "iat": int(issued_at.timestamp()),
            "jti": jwt.utils.base64url_encode(secrets.token_bytes(16)).decode(),
        },
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="widget_token.issue",
        entity="widget_token",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"allowed_origin": payload.allowed_origin, "ttl_minutes": ttl},
    )
    return {"token": signed, "expires_at": exp.isoformat() + "Z", "ttl_minutes": ttl}


@router.post("/tenants/{tenant_id}/widget-token/revoke", dependencies=[Depends(_ensure_super_admin())])
def revoke_widget_tokens_admin(tenant_id: str, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    now = datetime.datetime.now(datetime.timezone.utc)
    branding["widget_tokens_revoked_before"] = now.isoformat()
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="widget_token.revoke_all",
        entity="widget_token",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"revoked_before": branding.get("widget_tokens_revoked_before")},
    )
    return {"tenant_id": str(tenant.id), "revoked_before": branding.get("widget_tokens_revoked_before")}


@router.get("/overview", dependencies=[Depends(_ensure_super_admin())])
def admin_overview(db=Depends(get_db)):
    total_tenants = db.query(func.count(Tenant.id)).scalar() or 0
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    ia_cost = db.query(func.sum(IAUsage.cost_eur)).scalar() or 0
    return {
        "tenants": int(total_tenants),
        "leads": int(total_leads),
        "ia_cost_month": float(ia_cost or 0),
        "status": "ok",
    }


@router.get("/alerts", dependencies=[Depends(_ensure_super_admin())])
def admin_alerts(db=Depends(get_db)):
    tenants = db.query(Tenant).all()
    alerts = []
    for t in tenants:
        usage = float(getattr(t, "usage_monthly", 0) or 0)
        limit = float(getattr(t, "usage_limit_monthly", 0) or 0) or float(getattr(t, "ia_monthly_limit_eur", 0) or 0) or 0
        mode = (getattr(t, "usage_mode", "") or "").upper()
        if limit and usage >= 0.8 * limit:
            alerts.append(
                {
                    "tenant_id": str(t.id),
                    "tenant": t.name,
                    "type": "ia_usage_high",
                    "message": f"Uso IA {usage:.2f}/{limit:.2f} EUR",
                    "severity": "warning",
                }
            )
        if mode == "LOCKED":
            alerts.append(
                {
                    "tenant_id": str(t.id),
                    "tenant": t.name,
                    "type": "tenant_locked",
                    "message": "Tenant en modo LOCKED",
                    "severity": "critical",
                }
            )
        if str(getattr(t, "billing_status", "") or "").upper() in {"PAST_DUE", "CANCELED", "INCOMPLETE"}:
            alerts.append(
                {
                    "tenant_id": str(t.id),
                    "tenant": t.name,
                    "type": "billing_issue",
                    "message": f"Billing {t.billing_status}",
                    "severity": "warning",
                }
            )
    return {"items": alerts}


@router.get("/errors/recent", dependencies=[Depends(_ensure_super_admin())])
def recent_errors():
    log_path = Path(LOG_DIR) / "app.log"
    items: list[dict[str, Any]] = []
    if not log_path.exists():
        return {"items": items}
    try:
        with log_path.open() as fh:
            lines = fh.readlines()[-200:]  # leer cola y filtrar
        for line in reversed(lines):
            try:
                record = json.loads(line.strip())
            except Exception:
                continue
            level = (record.get("level") or "").upper()
            if level not in {"WARNING", "ERROR", "CRITICAL"}:
                continue
            msg = record.get("message") or {}
            payload = msg if isinstance(msg, dict) else {"message": msg}
            items.append(
                {
                    "timestamp": record.get("time"),
                    "level": level,
                    "service": "api",
                    "tenant_id": payload.get("tenant_id"),
                    "message": payload.get("message") or payload.get("event") or str(payload),
                }
            )
            if len(items) >= 50:
                break
    except Exception:
        return {"items": []}
    items.reverse()
    return {"items": items}


@router.get("/health", dependencies=[Depends(_ensure_super_admin())])
def admin_health():
    settings = get_settings()
    status_map = {"api": "UP", "db": "OK", "redis": "OK", "ia_provider": "OK"}

    # DB ping
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
    except Exception:
        status_map["db"] = "DEGRADED"
    finally:
        try:
            db.close()
        except Exception:
            pass

    # Redis ping
    try:
        import redis  # type: ignore

        client = redis.Redis.from_url(settings.redis_url, socket_timeout=0.2)
        client.ping()
    except Exception:
        status_map["redis"] = "DEGRADED"

    # IA provider: simple check clave presente
    if not settings.openai_api_key:
        status_map["ia_provider"] = "DEGRADED"

    return status_map


@router.post("/impersonate/{tenant_id}", dependencies=[Depends(_ensure_super_admin())])
def impersonate_tenant(tenant_id: str, request: Request, db=Depends(get_db)):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="jwt_secret_not_configured",
        )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    token = jwt.encode(
        {
            "type": "TENANT",
            "tenant_id": str(tenant.id),
            "impersonate_tenant_id": str(tenant.id),
            "roles": [UserRole.ADMIN.value, "IMPERSONATED"],
            "exp": exp,
            "jti": jwt.utils.base64url_encode(secrets.token_bytes(16)).decode(),
        },
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.impersonate",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"impersonate": str(tenant.id)},
    )
    return {"token": token, "expires_at": exp.isoformat() + "Z"}


@router.post("/tenants/{tenant_id}/exclude", dependencies=[Depends(_ensure_super_admin())])
def exclude_tenant(tenant_id: str, payload: TenantExclude, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    branding["excluded"] = True
    branding["excluded_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if payload.reason:
        branding["excluded_reason"] = payload.reason
    tenant.branding = branding
    tenant.ia_enabled = False
    tenant.use_ia = False
    try:
        tenant.usage_mode = UsageMode.LOCKED  # type: ignore
    except Exception:
        pass
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.exclude",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"reason": payload.reason},
    )
    return {"tenant_id": str(tenant.id), "excluded": True}


@router.post("/tenants/{tenant_id}/magic-login", dependencies=[Depends(_ensure_super_admin())])
def issue_magic_login(tenant_id: str, payload: MagicLinkRequest, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    email = (payload.email or "").strip() or (tenant.contact_email or "").strip()
    if not email:
        # Fallback: si ya existe un usuario (OWNER/ADMIN) pero no hay contact_email, usar su email.
        try:
            preferred = (
                db.query(User)
                .filter(User.tenant_id == tenant.id)
                .order_by(
                    sa.case((User.role == UserRole.OWNER.value, 0), else_=1),
                    User.created_at.asc(),
                )
                .first()
            )
        except Exception:
            preferred = None
        if preferred and getattr(preferred, "email", None):
            email = str(preferred.email).strip()
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing_email")
    user = db.query(User).filter(User.tenant_id == tenant.id, User.email == email).first()
    if not user:
        user = User(
            tenant_id=tenant.id,
            email=email,
            role=UserRole.OWNER.value,
            hashed_password=None,
            must_set_password=True,
            status="ACTIVE",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.must_set_password = True
        user.hashed_password = None
        db.add(user)
        db.commit()
        db.refresh(user)
    token, exp = _issue_magic_login_token(user, tenant, db)
    _send_magic_link_email(email, token, exp)
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    AuditService.log_admin_action(
        actor=actor,
        action="magic_link.issued",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"email": email, "expires_at": exp.isoformat() + "Z"},
    )
    return {"token": token, "expires_at": exp.isoformat() + "Z", "email": email}
