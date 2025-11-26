import datetime
import jwt
import uuid
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import oauth2_scheme, require_auth
from app.middleware.authz import require_any_role
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.models.tenants import Tenant
from app.services.key_manager import KeyManager

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

    ttl = min(max(payload.ttl_minutes, 5), 120)  # expiración corta para widget
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
        minutes=min(max(payload.ttl_minutes, 5), 180)
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
