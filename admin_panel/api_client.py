import os
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8100").rstrip("/")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")


def _headers(token: str | None = None, api_key: str | None = None) -> dict:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def admin_login(id_token: str):
    if ADMIN_API_KEY:
        # Bypass OIDC using static admin API key
        return {"api_key": ADMIN_API_KEY}
    resp = requests.post(f"{API_BASE}/v1/admin/auth/login", json={"id_token": id_token}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def list_tenants(token: str):
    resp = requests.get(f"{API_BASE}/v1/admin/tenants", headers=_headers(token, ADMIN_API_KEY), timeout=10)
    return resp.json() if resp.ok else []


def create_tenant(token: str, payload: dict):
    resp = requests.post(f"{API_BASE}/v1/admin/tenants", json=payload, headers=_headers(token, ADMIN_API_KEY), timeout=10)
    return resp.json() if resp.ok else {"error": resp.text}


def update_tenant(token: str, tenant_id: str, payload: dict):
    resp = requests.patch(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}", json=payload, headers=_headers(token, ADMIN_API_KEY), timeout=10
    )
    return resp.json() if resp.ok else {"error": resp.text}


def toggle_maintenance(token: str, tenant_id: str, maintenance: bool):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/maintenance",
        params={"maintenance": maintenance},
        headers=_headers(token, ADMIN_API_KEY),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text}


def issue_widget_token(token: str, tenant_id: str, allowed_origin: str, ttl_minutes: int = 30):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/widget-token",
        json={"allowed_origin": allowed_origin, "ttl_minutes": ttl_minutes},
        headers=_headers(token, ADMIN_API_KEY),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text}


def admin_overview(token: str):
    resp = requests.get(f"{API_BASE}/v1/admin/overview", headers=_headers(token, ADMIN_API_KEY), timeout=10)
    return resp.json() if resp.ok else {}


def impersonate(token: str, tenant_id: str):
    resp = requests.post(
        f"{API_BASE}/v1/admin/impersonate/{tenant_id}", headers=_headers(token, ADMIN_API_KEY), timeout=10
    )
    return resp.json() if resp.ok else {"error": resp.text}
