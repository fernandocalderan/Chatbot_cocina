import os
from fastapi import FastAPI

from app.api.appointments import router as appointments_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.files import router as files_router
from app.api.flows import router as flows_router
from app.api.leads import router as leads_router
from app.api.metrics import router as metrics_router
from app.api.scoring import router as scoring_router
from app.api.sessions import router as sessions_router
from app.api.tenant import router as tenant_router
from app.core.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.rate_limiter import add_request_context
from app.middleware.tenant_resolver import resolve_tenant
from app.core.logger import setup_logger

settings = get_settings()
setup_logger()
API_PREFIX = "/v1"


def get_application() -> FastAPI:
    app = FastAPI(
        title=f"{settings.app_name} - API v1",
        description="Endpoints versionados bajo el prefijo /v1.",
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    # CORS
    origins = []
    env_origins = os.getenv("CORS_ORIGINS")
    cors_raw = env_origins if env_origins is not None else settings.cors_origins
    if cors_raw:
        origins = [o.strip() for o in cors_raw.split(",") if o.strip()]
    elif settings.environment == "local":
        # Permitir CORS en local para el widget (Vite suele usar 5173/5174)
        origins = [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.middleware("http")(resolve_tenant)
    app.middleware("http")(add_request_context)

    app.include_router(health_router, prefix=API_PREFIX)
    app.include_router(auth_router, prefix=API_PREFIX)
    app.include_router(flows_router, prefix=API_PREFIX)
    app.include_router(chat_router, prefix=API_PREFIX)
    app.include_router(sessions_router, prefix=API_PREFIX)
    app.include_router(files_router, prefix=API_PREFIX)
    app.include_router(tenant_router, prefix=API_PREFIX)
    app.include_router(appointments_router, prefix=API_PREFIX)
    app.include_router(leads_router, prefix=API_PREFIX)
    app.include_router(metrics_router, prefix=API_PREFIX)
    app.include_router(scoring_router, prefix=API_PREFIX)
    return app


app = get_application()
