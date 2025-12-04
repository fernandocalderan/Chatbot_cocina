from fastapi import APIRouter

from app.api.appointments import router as appointments_router
from app.api.files import router as files_router
from app.api.flows import router as flows_router
from app.api.leads import router as leads_router
from app.api.v1.endpoints.metrics_ia import router as metrics_ia_router
from app.api.v1.endpoints.tenant_ia_settings import (
    router as tenant_ia_settings_router,
)
from app.api.v1.endpoints.billing import router as billing_router
from app.api.v1.endpoints.stripe_webhook import router as stripe_webhook_router
from app.api.v1.endpoints.tenants_admin import router as tenants_admin_router

api_router = APIRouter()

api_router.include_router(leads_router, prefix="/leads", tags=["leads"])
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(flows_router, prefix="/flows", tags=["flows"])

# === MÉTRICAS IA (SOLO SUPER_ADMIN) ===
api_router.include_router(
    metrics_ia_router,
    prefix="",
    tags=["metrics", "ia"],
)

# === IA SETTINGS POR TENANT (SOLO SUPER_ADMIN) ===
api_router.include_router(
    tenant_ia_settings_router,
    prefix="",
    tags=["tenant", "ia", "settings"],
)
api_router.include_router(
    billing_router,
    prefix="",
    tags=["billing"],
)
api_router.include_router(
    stripe_webhook_router,
    prefix="",
    tags=["billing"],
)
api_router.include_router(
    tenants_admin_router,
    prefix="",
    tags=["tenants"],
)
