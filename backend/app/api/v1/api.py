from fastapi import APIRouter

from app.api.appointments import router as appointments_router
from app.api.files import router as files_router
from app.api.flows import router as flows_router
from app.api.leads import router as leads_router
from app.api.v1.endpoints.metrics_ia import router as metrics_ia_router

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
