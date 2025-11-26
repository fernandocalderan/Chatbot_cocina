import datetime
import uuid

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.security import verify_password
from app.models.users import User
from app.services.key_manager import KeyManager
from app.services.jwt_blacklist import JWTBlacklist

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)


class LoginInput(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginInput, request: Request, db: Session = Depends(get_db)):
    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="tenant_not_resolved"
        )

    user = (
        db.query(User)
        .filter(User.email == payload.email, User.tenant_id == tenant_id)
        .first()
    )
    if (
        not user
        or not user.hashed_password
        or not verify_password(payload.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        )
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=500, detail="jwt_secret_not_configured")
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    payload_token = {
        "sub": str(user.id),
        "tenant_id": str(tenant_id),
        "roles": [user.role] if user.role else [],
        "type": "access",
        "exp": exp,
        "jti": str(uuid.uuid4()),
    }
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    token = jwt.encode(
        payload_token,
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    return {"access_token": token, "token_type": "bearer"}


async def require_auth(
    token: str | None = Depends(oauth2_scheme),
    x_api_key: str | None = Header(default=None),
):
    settings = get_settings()
    # Si hay API token configurado, permitirlo
    if settings.panel_api_token and x_api_key == settings.panel_api_token:
        return True

    # JWT obligatorio si jwt_secret está configurado
    if settings.jwt_secret:
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
            payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
            )
        jti = payload.get("jti")
        if jti and JWTBlacklist(km.redis_url).is_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="token_revoked"
            )
        return True

    # Si no hay secretos configurados, dejar pasar (modo dev)
    return True
