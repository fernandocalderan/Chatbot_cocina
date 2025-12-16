import datetime
import uuid
import os
import hashlib

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.security import verify_password, get_password_hash
from app.models.users import User
from app.services.key_manager import KeyManager
from app.services.jwt_blacklist import JWTBlacklist
from app.models.login_tokens import LoginToken
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)


class LoginInput(BaseModel):
    email: str
    password: str


class SetPasswordInput(BaseModel):
    password: str
    password_confirm: str


def _issue_session_token(user: User, tenant_id: str, hours: int = 24) -> str:
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=500, detail="jwt_secret_not_configured")
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    role = (user.role or "").upper()
    payload_token = {
        "sub": str(user.id),
        "tenant_id": str(tenant_id),
        "roles": [role] if role else [],
        "type": "TENANT",
        "exp": exp,
        "jti": str(uuid.uuid4()),
        "must_set_password": bool(getattr(user, "must_set_password", False)),
    }
    km = KeyManager()
    current_kid, current_secret, _ = km.get_jwt_keys()
    token = jwt.encode(
        payload_token,
        current_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": current_kid},
    )
    return token


def _validate_password_strength(pwd: str) -> None:
    if len(pwd) < 10:
        raise HTTPException(status_code=400, detail="password_too_short")
    if not any(c.isupper() for c in pwd):
        raise HTTPException(status_code=400, detail="password_needs_uppercase")
    if not any(c.isdigit() for c in pwd):
        raise HTTPException(status_code=400, detail="password_needs_number")
    if not any(not c.isalnum() for c in pwd):
        raise HTTPException(status_code=400, detail="password_needs_symbol")


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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        )
    if getattr(user, "must_set_password", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="must_set_password_first")
    if not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        )
    if (user.status or "").upper() == "DISABLED":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user_disabled")
    if getattr(user, "must_set_password", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="must_set_password_first")
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=500, detail="jwt_secret_not_configured")
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    role = (user.role or "").upper()
    payload_token = {
        "sub": str(user.id),
        "tenant_id": str(tenant_id),
        "roles": [role] if role else [],
        "type": "TENANT",
        "exp": exp,
        "jti": str(uuid.uuid4()),
        "must_set_password": bool(getattr(user, "must_set_password", False)),
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


@router.get("/magic-login")
def magic_login(token: str = Query(...), db: Session = Depends(get_db)):
    settings = get_settings()
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    if payload.get("scope") != "tenant_magic_login":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_scope")
    user_id = payload.get("user_id")
    tenant_id = payload.get("tenant_id")
    if not user_id or not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.datetime.now(datetime.timezone.utc)
    login_token = (
        db.query(LoginToken)
        .filter(LoginToken.token_hash == token_hash, LoginToken.expires_at >= now, LoginToken.used_at.is_(None))
        .first()
    )
    if not login_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token_expired_or_used")
    login_token.used_at = now
    db.add(login_token)
    db.commit()
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")
    if (user.status or "").upper() == "DISABLED":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user_disabled")
    session_token = _issue_session_token(user, tenant_id)
    AuditService.log_admin_action(
        actor=user.email or str(user.id),
        action="magic_login.success",
        entity="user",
        entity_id=str(user.id),
        tenant_id=str(user.tenant_id),
        meta={"jti": login_token.jti},
    )
    return {"token": session_token, "must_set_password": bool(getattr(user, "must_set_password", False))}


@router.post("/set-password")
def set_password(payload: SetPasswordInput, token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token")
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail="password_mismatch")
    _validate_password_strength(payload.password)
    settings = get_settings()
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    try:
        data = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    user_id = data.get("sub")
    tenant_id = data.get("tenant_id")
    if not user_id or not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")
    if str(user.tenant_id) != str(tenant_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    if not getattr(user, "must_set_password", False):
        raise HTTPException(status_code=400, detail="password_already_set")
    user.hashed_password = get_password_hash(payload.password)
    user.must_set_password = False
    db.add(user)
    db.commit()
    AuditService.log_admin_action(
        actor=user.email or str(user.id),
        action="password.set",
        entity="user",
        entity_id=str(user.id),
        tenant_id=str(user.tenant_id),
        meta={"activated": True},
    )
    # Emitir nuevo token sin flag must_set_password
    session_token = _issue_session_token(user, tenant_id)
    return {"status": "ok", "token": session_token}


async def require_auth(
    token: str | None = Depends(oauth2_scheme),
    x_api_key: str | None = Header(default=None),
    request: Request = None,
):
    settings = get_settings()
    if os.getenv("DISABLE_DB") == "1":
        # Modo test: si hay token, validarlo; si hay x-api-key, bypass.
        if token:
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
        if x_api_key:
            return True
        return True
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
        if payload.get("must_set_password") and request:
            path = request.url.path if request.url else ""
            if not path.endswith("/auth/set-password"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="must_set_password_first"
                )
        return True

    # Si no hay secretos configurados, dejar pasar (modo dev)
    return True
