import datetime
import jwt
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.auth import oauth2_scheme, require_auth
from app.api.deps import get_db, get_tenant_id
from app.core.config import get_settings
from app.models.tenants import Tenant

router = APIRouter(prefix="/tenant", tags=["tenant"])


@router.get("/config", dependencies=[Depends(require_auth)])
def get_tenant_config(db=Depends(get_db), tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found")

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


@router.post("/widget/token", dependencies=[Depends(require_auth)])
def issue_widget_token_short(payload: WidgetTokenInput, tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="jwt_secret_not_configured")

    ttl = min(max(payload.ttl_minutes, 5), 120)  # expiración corta para widget
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ttl)
    data = {
        "type": "widget",
        "tenant_id": tenant_id,
        "allowed_origin": payload.allowed_origin,
        "exp": exp,
    }
    signed = jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"token": signed, "expires_at": exp.isoformat() + "Z", "ttl_minutes": ttl}


@router.post("/widget-token", dependencies=[Depends(require_auth)])
def issue_widget_token(payload: WidgetTokenInput, tenant_id: str = Depends(get_tenant_id), token: str = Depends(oauth2_scheme)):
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="jwt_secret_not_configured")

    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=min(max(payload.ttl_minutes, 5), 180))
    data = {
        "type": "widget",
        "tenant_id": tenant_id,
        "allowed_origin": payload.allowed_origin,
        "exp": exp,
    }
    signed = jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"token": signed, "expires_at": exp.isoformat() + "Z"}
