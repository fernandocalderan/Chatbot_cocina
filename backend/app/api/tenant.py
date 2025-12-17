import datetime
import jwt
import uuid
from pydantic import BaseModel
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.auth import oauth2_scheme, require_auth
from app.middleware.authz import require_any_role
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.models.tenants import Tenant, BillingStatus
from app.services.key_manager import KeyManager
from app.services.pricing import get_plan_limits
from app.services.billing_service import create_billing_portal_session, subscription_overview
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/tenant", tags=["tenant"])

_ALLOWED_LANGS = {"es", "pt", "en", "ca"}
_ALLOWED_CURRENCIES = {"EUR", "BRL", "USD"}


def _normalize_origin(origin: str) -> str | None:
    raw = (origin or "").strip()
    if not raw:
        return None
    try:
        u = urlparse(raw)
    except Exception:
        return None
    if u.scheme not in {"http", "https"}:
        return None
    if not u.netloc:
        return None
    if u.path or u.params or u.query or u.fragment:
        return None
    return f"{u.scheme}://{u.netloc}"


def _serialize_config(tenant: Tenant) -> dict:
    branding = getattr(tenant, "branding", {}) or {}
    currency = branding.get("currency") or branding.get("Currency") or "EUR"
    allowed = (
        branding.get("allowed_widget_origins")
        or branding.get("allowed_origins")
        or branding.get("allowedOrigins")
        or []
    )
    if not isinstance(allowed, list):
        allowed = []
    allowed_norm = [o for o in (_normalize_origin(str(x)) for x in allowed) if o]
    return {
        "tenant_id": str(tenant.id),
        "customer_code": getattr(tenant, "customer_code", None),
        "name": tenant.name,
        "logo_url": getattr(tenant, "logo_url", None),
        "theme": getattr(tenant, "theme", None) or "orange",
        "language": tenant.idioma_default or "es",
        "timezone": getattr(tenant, "timezone", None) or "Europe/Madrid",
        "currency": str(currency).upper(),
        "allowed_widget_origins": sorted(set(allowed_norm)),
        "texts": {
            "header_title": tenant.name or "Asistente virtual",
            "header_subtitle": "Resolvemos tus dudas",
        },
    }


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

    # Additivo: incluye timezone/currency/allowlist sin romper compatibilidad.
    return _serialize_config(tenant)


class TenantConfigUpdate(BaseModel):
    language: str | None = None
    timezone: str | None = None
    currency: str | None = None


@router.patch("/config", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def update_tenant_config(
    payload: TenantConfigUpdate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    if payload.language:
        lang = str(payload.language).lower()
        if lang not in _ALLOWED_LANGS:
            raise HTTPException(status_code=400, detail="invalid_language")
        tenant.idioma_default = lang
    if payload.timezone:
        tz = str(payload.timezone).strip()
        if not tz or len(tz) > 64:
            raise HTTPException(status_code=400, detail="invalid_timezone")
        tenant.timezone = tz
    if payload.currency:
        cur = str(payload.currency).upper().strip()
        if cur not in _ALLOWED_CURRENCIES:
            raise HTTPException(status_code=400, detail="invalid_currency")
        branding["currency"] = cur
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return _serialize_config(tenant)


class WidgetSettings(BaseModel):
    allowed_origins: list[str] | None = None


@router.get("/widget/settings", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def get_widget_settings(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    allowed = (
        branding.get("allowed_widget_origins")
        or branding.get("allowed_origins")
        or branding.get("allowedOrigins")
        or []
    )
    if not isinstance(allowed, list):
        allowed = []
    allowed_norm = [o for o in (_normalize_origin(str(x)) for x in allowed) if o]
    return {"allowed_origins": sorted(set(allowed_norm))}


@router.patch("/widget/settings", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def update_widget_settings(
    payload: WidgetSettings,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    token: str = Depends(oauth2_scheme),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")
    branding = getattr(tenant, "branding", {}) or {}
    allowed = payload.allowed_origins or []
    allowed_norm = [o for o in (_normalize_origin(str(x)) for x in allowed) if o]
    branding["allowed_widget_origins"] = sorted(set(allowed_norm))
    tenant.branding = branding
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return {"allowed_origins": branding.get("allowed_widget_origins") or []}


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

    ttl = min(max(payload.ttl_minutes, 15), 60)  # expiración corta para widget (<= 1h)
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
    normalized = _normalize_origin(payload.allowed_origin)
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_origin")
    if allowed and normalized not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="origin_not_allowed"
        )
    now_ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    data = {
        "type": "WIDGET",
        "tenant_id": tenant_id,
        "scope": "widget",
        "allowed_origin": normalized,
        "iat": now_ts,
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

    ttl = min(max(payload.ttl_minutes, 15), 60)
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
    normalized = _normalize_origin(payload.allowed_origin)
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_origin")
    if allowed and normalized not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="origin_not_allowed"
        )
    now_ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    data = {
        "type": "WIDGET",
        "tenant_id": tenant_id,
        "scope": "widget",
        "allowed_origin": normalized,
        "iat": now_ts,
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

    if (data.get("type") or "").upper() != "WIDGET":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid_token_type"
        )
    if (data.get("scope") or "widget").lower() != "widget":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid_token_scope")

    tenant_id = data.get("tenant_id")
    allowed_origin = data.get("allowed_origin")
    issued_at = data.get("iat")
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
    revoked_before = branding.get("widget_tokens_revoked_before")
    if revoked_before and issued_at:
        try:
            import datetime as _dt

            revoked_dt = _dt.datetime.fromisoformat(revoked_before)
            if _dt.datetime.fromtimestamp(int(issued_at), _dt.timezone.utc) < revoked_dt:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token_revoked",
                )
        except HTTPException:
            raise
        except Exception:
            pass
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
            "type": "WIDGET",
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
    quota_status = QuotaService.evaluate(db, tenant)

    return {
        "tenant_id": str(tenant.id),
        "plan": tenant.plan,
        "billing_status": getattr(tenant, "billing_status", BillingStatus.ACTIVE),
        "stripe_status": stripe_status,
        "current_period_end": renewal_at,
        "price_id": price_id,
        "limits": limits,
        "manage_url": portal_url,
        "quota_status": quota_status.to_dict() if quota_status else None,
    }
