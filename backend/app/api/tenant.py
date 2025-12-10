import datetime
import jwt
import uuid
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.auth import oauth2_scheme, require_auth
from app.middleware.authz import require_any_role
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.models.tenants import Tenant, BillingStatus
from app.services.key_manager import KeyManager
from app.services.pricing import get_plan_limits
from app.services.billing_service import create_billing_portal_session, subscription_overview

router = APIRouter(prefix="/tenant", tags=["tenant"])


@router.get("/config", dependencies=[Depends(require_auth)])
def get_tenant_config(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found"
        )

    # En una versión posterior, esto leerá configuración personalizada por tenant (logo, colores, textos, idioma).
    return {
        "tenant_id": str(tenant.id),
        "name": tenant.name,
        "logo_url": getattr(tenant, "logo_url", None),
        "theme": getattr(tenant, "theme", None) or "orange",
        "language": tenant.idioma_default or "es",
        "texts": {
            "header_title": tenant.name or "Asistente virtual",
            "header_subtitle": "Resolvemos tus dudas",
        },
    }


class WidgetTokenInput(BaseModel):
    allowed_origin: str
    ttl_minutes: int = 60


class WidgetTokenRenewInput(BaseModel):
    ttl_minutes: int | None = None


@router.post(
    "/widget/token", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))]
)
def issue_widget_token_short(
    payload: WidgetTokenInput,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
    ):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="jwt_secret_not_configured",
        )

    ttl = min(max(payload.ttl_minutes, 15), 60)  # expiración corta para widget
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ttl)
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first() if db else None
    allowed = []
    if tenant:
        branding = getattr(tenant, "branding", {}) or {}
        allowed = (
            branding.get("allowed_widget_origins")
            or branding.get("allowed_origins")
            or []
        )
    if allowed and payload.allowed_origin not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="origin_not_allowed"
        )
    data = {
        "type": "widget",
        "tenant_id": tenant_id,
        "allowed_origin": payload.allowed_origin,
        "exp": exp,
        "jti": str(uuid.uuid4()),
    }
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    signed = jwt.encode(
        data,
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    return {"token": signed, "expires_at": exp.isoformat() + "Z", "ttl_minutes": ttl}


@router.post(
    "/widget-token", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))]
)
def issue_widget_token(
    payload: WidgetTokenInput,
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="jwt_secret_not_configured",
        )

    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=min(max(payload.ttl_minutes, 15), 60)
    )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first() if db else None
    allowed = []
    if tenant:
        branding = getattr(tenant, "branding", {}) or {}
        allowed = (
            branding.get("allowed_widget_origins")
            or branding.get("allowed_origins")
            or []
        )
    if allowed and payload.allowed_origin not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="origin_not_allowed"
        )
    data = {
        "type": "widget",
        "tenant_id": tenant_id,
        "allowed_origin": payload.allowed_origin,
        "exp": exp,
        "jti": str(uuid.uuid4()),
    }
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    signed = jwt.encode(
        data,
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    return {"token": signed, "expires_at": exp.isoformat() + "Z"}


@router.post("/widget/token/renew")
def renew_widget_token(
    payload: WidgetTokenRenewInput | None,
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db=Depends(get_db),
):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="jwt_secret_not_configured",
        )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token"
        )
    km = KeyManager()
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid") or "current"
    except Exception:
        kid = "current"
    current_kid, current_secret, previous = km.get_jwt_keys()
    secrets_map = {current_kid: current_secret}
    secrets_map.update(previous)
    secret = secrets_map.get(kid)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )
    try:
        data = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )

    if data.get("type") != "widget":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid_token_type"
        )

    tenant_id = data.get("tenant_id")
    allowed_origin = data.get("allowed_origin")
    if not tenant_id or not allowed_origin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )

    origin = request.headers.get("Origin") or request.headers.get("origin") or ""
    referer = request.headers.get("Referer") or request.headers.get("referer") or ""
    if origin or referer:
        if not (origin.startswith(allowed_origin) or referer.startswith(allowed_origin)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="origin_not_allowed"
            )

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first() if db else None
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found"
        )
    branding = getattr(tenant, "branding", {}) or {}
    allowed = (
        branding.get("allowed_widget_origins")
        or branding.get("allowed_origins")
        or branding.get("allowedOrigins")
        or []
    )
    if allowed and allowed_origin not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="origin_not_allowed"
        )

    ttl_req = payload.ttl_minutes if payload else None
    ttl_minutes = min(max(ttl_req or 30, 15), 60)
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=ttl_minutes
    )
    new_token = jwt.encode(
        {
            "type": "widget",
            "tenant_id": tenant_id,
            "allowed_origin": allowed_origin,
            "exp": exp,
            "jti": str(uuid.uuid4()),
        },
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    return {"token": new_token, "expires_at": exp.isoformat() + "Z", "ttl_minutes": ttl_minutes}


@router.get("/me/billing", dependencies=[Depends(require_auth)])
def get_billing_overview(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found"
        )
    settings = get_settings()
    limits = get_plan_limits(tenant.plan)
    renewal_at = None
    stripe_status = None
    price_id = None
    if settings.stripe_api_key and tenant.stripe_subscription_id:
        info = subscription_overview(tenant.stripe_subscription_id) or {}
        stripe_status = info.get("stripe_status")
        price_id = info.get("price_id")
        ts = info.get("current_period_end")
        if ts:
            try:
                renewal_at = (
                    datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
                ).isoformat()
            except Exception:
                renewal_at = None
    portal_url = None
    if settings.stripe_api_key and tenant.stripe_customer_id:
        try:
            portal_url = create_billing_portal_session(tenant.stripe_customer_id)
        except Exception:
            portal_url = None

    return {
        "tenant_id": str(tenant.id),
        "plan": tenant.plan,
        "billing_status": getattr(tenant, "billing_status", BillingStatus.ACTIVE),
        "stripe_status": stripe_status,
        "current_period_end": renewal_at,
        "price_id": price_id,
        "limits": limits,
        "manage_url": portal_url,
    }
