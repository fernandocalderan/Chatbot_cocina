from __future__ import annotations

import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.auth import require_auth
from app.api.deps import get_db, get_tenant_id
from app.models.tenants import Tenant

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _get_google_client():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return client_id, client_secret, redirect_uri


def _get_ms_client():
    client_id = os.getenv("MS_CLIENT_ID")
    client_secret = os.getenv("MS_CLIENT_SECRET")
    redirect_uri = os.getenv("MS_REDIRECT_URI")
    tenant = os.getenv("MS_TENANT_ID", "common")
    return client_id, client_secret, redirect_uri, tenant


@router.get("/google/auth-url", dependencies=[Depends(require_auth)])
def google_auth_url(state: Optional[str] = Query(default=None)):
    client_id, _, redirect_uri = _get_google_client()
    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="google_not_configured",
        )
    scopes = [
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.readonly",
    ]
    state_val = state or secrets.token_urlsafe(16)
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code&access_type=offline&prompt=consent"
        f"&scope={' '.join(scopes)}&state={state_val}"
    )
    return {"auth_url": url, "state": state_val}


@router.get("/google/callback", dependencies=[Depends(require_auth)])
def google_callback(
    request: Request,
    code: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _, client_secret, redirect_uri = _get_google_client()
    if not client_secret or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="google_not_configured",
        )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found"
        )
    # Stub: no llamada externa, guardamos token simulado
    refresh_token = f"google-refresh-{code}"
    tenant.google_refresh_token = refresh_token
    tenant.google_calendar_connected = True
    db.add(tenant)
    db.commit()
    return {"connected": True}


@router.get("/microsoft/auth-url", dependencies=[Depends(require_auth)])
def microsoft_auth_url(state: Optional[str] = Query(default=None)):
    client_id, _, redirect_uri, tenant = _get_ms_client()
    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="microsoft_not_configured",
        )
    scopes = ["offline_access", "Calendars.ReadWrite", "User.Read"]
    state_val = state or secrets.token_urlsafe(16)
    url = (
        f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        f"?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}"
        f"&scope={' '.join(scopes)}&state={state_val}"
    )
    return {"auth_url": url, "state": state_val}


@router.get("/microsoft/callback", dependencies=[Depends(require_auth)])
def microsoft_callback(
    request: Request,
    code: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _, client_secret, redirect_uri, _ = _get_ms_client()
    if not client_secret or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="microsoft_not_configured",
        )
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tenant_not_found"
        )
    refresh_token = f"ms-refresh-{code}"
    tenant.microsoft_refresh_token = refresh_token
    tenant.microsoft_calendar_connected = True
    db.add(tenant)
    db.commit()
    return {"connected": True}
