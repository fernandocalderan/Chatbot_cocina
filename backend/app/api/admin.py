import datetime
import secrets
from typing import Any, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func

from app.api.deps import get_db
from app.core.config import get_settings
from app.middleware.authz import require_role
from app.models.ia_usage import IAUsage
from app.models.leads import Lead
from app.models.tenants import Tenant
from app.models.users import UserRole
from app.models.audits import AuditLog
from app.services.key_manager import KeyManager
from app.services.oidc_admin import validate_admin_id_token, OIDCValidationError
from app.services.template_service import TemplateService

router = APIRouter(prefix="/admin", tags=["admin"])


def _ensure_super_admin():
    return require_role(UserRole.SUPER_ADMIN.value)


def _log_admin_action(db, tenant_id, entity: str, action: str, actor: str | None = None, meta: dict | None = None):
    if db is None or tenant_id is None:
        return
    log = AuditLog(
        tenant_id=tenant_id,
        entity=entity,
        entity_id=str(tenant_id),
        action=action,
        actor=actor,
        meta_data=meta or {},
    )
    db.add(log)
    try:
        db.commit()
    except Exception:
        db.rollback()


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
    use_ia: Optional[bool] = None
    ia_enabled: Optional[bool] = None


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
    use_ia: Optional[bool] = None
    ia_enabled: Optional[bool] = None


class WidgetTokenRequest(BaseModel):
    allowed_origin: str
    ttl_minutes: int = 30


def _serialize_tenant(t: Tenant) -> dict[str, Any]:
    branding = getattr(t, "branding", {}) or {}
    return {
        "id": str(t.id),
        "name": t.name,
        "contact_email": t.contact_email,
        "plan": t.plan,
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
    }


@router.get("/tenants", dependencies=[Depends(_ensure_super_admin())])
def list_tenants(db=Depends(get_db)):
    tenants = db.query(Tenant).all()
    return [_serialize_tenant(t) for t in tenants]


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
    branding = {
        "allowed_widget_origins": payload.allowed_origins or [],
        "maintenance": payload.maintenance,
    }
    tenant = Tenant(
        name=payload.name,
        contact_email=payload.contact_email,
        plan=payload.plan,
        ia_monthly_limit_eur=payload.ia_monthly_limit_eur,
        usage_limit_monthly=payload.usage_limit_monthly,
        branding=branding,
        use_ia=payload.use_ia if payload.use_ia is not None else True,
        ia_enabled=payload.ia_enabled if payload.ia_enabled is not None else True,
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
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    _log_admin_action(db, tenant.id, "tenant", "create", actor=actor, meta={"plan": tenant.plan})
    return _serialize_tenant(tenant)


@router.patch("/tenants/{tenant_id}", dependencies=[Depends(_ensure_super_admin())])
def update_tenant(tenant_id: str, payload: TenantUpdate, request: Request, db=Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    if payload.allowed_origins is not None:
        branding["allowed_widget_origins"] = payload.allowed_origins
    if payload.maintenance is not None:
        branding["maintenance"] = bool(payload.maintenance)
        branding["maintenance_mode"] = bool(payload.maintenance)
    for field, value in payload.model_dump(exclude_none=True, exclude={"allowed_origins", "maintenance"}).items():
        setattr(tenant, field, value)
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    _log_admin_action(db, tenant.id, "tenant", "update", actor=actor, meta=payload.model_dump(exclude_none=True))
    return _serialize_tenant(tenant)


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
    _log_admin_action(db, tenant.id, "tenant", "maintenance", actor=actor, meta={"maintenance": bool(maintenance)})
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
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    signed = jwt.encode(
        {
            "type": "WIDGET",
            "tenant_id": tenant_id,
            "allowed_origin": payload.allowed_origin,
            "exp": exp,
            "jti": jwt.utils.base64url_encode(secrets.token_bytes(16)).decode(),
        },
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    actor = _resolve_actor(request.headers.get("Authorization"), request.headers.get("x-api-key"))
    _log_admin_action(
        db,
        tenant.id,
        "widget_token",
        "issue",
        actor=actor,
        meta={"allowed_origin": payload.allowed_origin, "ttl_minutes": ttl},
    )
    return {"token": signed, "expires_at": exp.isoformat() + "Z", "ttl_minutes": ttl}


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


@router.get("/errors/recent", dependencies=[Depends(_ensure_super_admin())])
def recent_errors():
    # Placeholder: integrar con sistema de logs externo (CloudWatch/Loki)
    return {"items": []}


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
    _log_admin_action(
        db,
        tenant.id,
        "tenant",
        "impersonate",
        actor=actor,
        meta={"impersonate": str(tenant.id)},
    )
    return {"token": token, "expires_at": exp.isoformat() + "Z"}
