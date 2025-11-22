from fastapi import FastAPI

from app.api.appointments import router as appointments_router
from app.api.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.flows import router as flows_router
from app.api.leads import router as leads_router
from app.core.config import get_settings

settings = get_settings()


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(health_router)
    app.include_router(flows_router)
    app.include_router(chat_router)
    app.include_router(appointments_router)
    app.include_router(leads_router)
    return app


app = get_application()
