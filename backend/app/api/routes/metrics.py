from fastapi import APIRouter, Header, HTTPException, Response, status

from app.core.config import get_settings
from app.observability.metrics import export_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", summary="Metrics endpoint")
def read_metrics(x_api_key: str | None = Header(default=None)):
    settings = get_settings()
    # Permitir solo en local o con API key
    if settings.environment != "local":
        if not settings.panel_api_token or x_api_key != settings.panel_api_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return Response(
        content=export_metrics(),
        media_type="text/plain; version=0.0.4",
    )
