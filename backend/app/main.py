from fastapi import FastAPI

from app.api.appointments import router as appointments_router
from app.api.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.flows import router as flows_router
from app.api.leads import router as leads_router
from app.core.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.rate_limiter import add_request_context

settings = get_settings()


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    # CORS
    origins = []
    if settings.cors_origins:
        origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.middleware("http")(add_request_context)

    app.include_router(health_router)
    app.include_router(flows_router)
    app.include_router(chat_router)
    app.include_router(appointments_router)
    app.include_router(leads_router)
    return app


app = get_application()
