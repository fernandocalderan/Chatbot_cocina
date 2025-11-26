from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.authz import require_any_role
from app.services.key_manager import KeyManager
from app.services.jwt_blacklist import JWTBlacklist

router = APIRouter(prefix="/security", tags=["security"])


@router.post("/rotate-keys", dependencies=[Depends(require_any_role("OWNER", "ADMIN"))])
def rotate_keys(payload: dict):
    new_jwt_secret = payload.get("new_jwt_secret")
    new_jwt_kid = payload.get("new_jwt_kid")
    new_pii_key = payload.get("new_pii_key")
    if not (new_jwt_secret and new_jwt_kid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="missing_keys"
        )
    km = KeyManager()
    km.rotate_jwt_keys(new_jwt_kid, new_jwt_secret)
    if new_pii_key:
        km.rotate_pii_keys(new_pii_key)
    blacklist = JWTBlacklist(km.redis_url)
    blacklist.blacklist_token("global_rotated", float("inf"))
    return {"status": "rotated"}
