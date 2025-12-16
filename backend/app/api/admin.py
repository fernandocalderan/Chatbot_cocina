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
from app.models.leads import Lead
from app.models.tenants import Tenant, UsageMode
from app.models.users import UserRole, User
from app.models.login_tokens import LoginToken
from app.services.key_manager import KeyManager
from app.services.oidc_admin import validate_admin_id_token, OIDCValidationError
from app.services.template_service import TemplateService
from app.services.audit_service import AuditService
from app.services.email_service import send_magic_link
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


class WidgetTokenRequest(BaseModel):
    allowed_origin: str
    ttl_minutes: int = 30


class TenantExclude(BaseModel):
    reason: Optional[str] = None


class MagicLinkRequest(BaseModel):
    email: Optional[str] = None


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
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.create",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"plan": tenant.plan},
    )
    AuditService.log_admin_action(
        actor=actor,
        action="tenant.customer_code_assigned",
        entity="tenant",
        entity_id=str(tenant.id),
        tenant_id=str(tenant.id),
        meta={"customer_code": customer_code},
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
    for field, value in payload.model_dump(exclude_none=True, exclude={"allowed_origins", "maintenance"}).items():
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
    email = payload.email or tenant.contact_email
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
