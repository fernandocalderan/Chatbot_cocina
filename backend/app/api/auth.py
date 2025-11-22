from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_panel_token(x_api_key: str | None = Header(default=None)):
    settings = get_settings()
    if settings.panel_api_token:
        if x_api_key != settings.panel_api_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    return True
