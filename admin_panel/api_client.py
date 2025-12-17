import os
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8100").rstrip("/")


def _load_local_admin_api_key() -> str | None:
    """
    Conveniencia en local:
    - Si no hay key en env, intenta leerla desde ../backend/.env.
    - Solo aplica cuando API_BASE apunta a localhost/127.0.0.1.
    """
    if "localhost" not in API_BASE and "127.0.0.1" not in API_BASE:
        return None
    try:
        here = os.path.dirname(__file__)
        env_path = os.path.abspath(os.path.join(here, "..", "backend", ".env"))
        if not os.path.exists(env_path):
            return None
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("ADMIN_API_KEY=") or line.startswith("ADMIN_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        return None
    return None


def _admin_api_key() -> str | None:
    return (
        os.getenv("ADMIN_API_KEY")
        or os.getenv("ADMIN_API_TOKEN")
        or _load_local_admin_api_key()
    )


def resolve_admin_api_key() -> str | None:
    return _admin_api_key()


def _headers(token: str | None = None, api_key: str | None = None) -> dict:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def admin_login(id_token: str):
    key = _admin_api_key()
    if key:
        # Bypass OIDC using static admin API key
        return {"api_key": key}
    resp = requests.post(f"{API_BASE}/v1/admin/auth/login", json={"id_token": id_token}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def list_tenants(token: str | None, search: str | None = None, api_key: str | None = None):
    params = {"search": search} if search else None
    resp = requests.get(
        f"{API_BASE}/v1/admin/tenants",
        headers=_headers(token, api_key or _admin_api_key()),
        params=params,
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def create_tenant(token: str | None, payload: dict, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def update_tenant(token: str | None, tenant_id: str, payload: dict, api_key: str | None = None):
    resp = requests.patch(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def toggle_maintenance(token: str | None, tenant_id: str, maintenance: bool, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/maintenance",
        params={"maintenance": maintenance},
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def issue_widget_token(
    token: str | None, tenant_id: str, allowed_origin: str, ttl_minutes: int = 30, api_key: str | None = None
):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/widget-token",
        json={"allowed_origin": allowed_origin, "ttl_minutes": ttl_minutes},
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def admin_overview(token: str | None, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/overview",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def list_verticals(token: str | None, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/verticals",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {"items": [], "error": resp.text, "status_code": resp.status_code}


def get_vertical(token: str | None, vertical_key: str, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def admin_health(token: str | None, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/health",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def admin_recent_errors(token: str | None, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/errors/recent",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {"items": [], "error": resp.text, "status_code": resp.status_code}


def admin_alerts(token: str | None, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/alerts",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {"items": [], "error": resp.text, "status_code": resp.status_code}


def impersonate(token: str | None, tenant_id: str, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/impersonate/{tenant_id}",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def revoke_widget_tokens(token: str | None, tenant_id: str, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/widget-token/revoke",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def exclude_tenant(token: str | None, tenant_id: str, reason: str | None = None, api_key: str | None = None):
    payload = {"reason": reason} if reason else {}
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/exclude",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def issue_magic_link(token: str | None, tenant_id: str, email: str | None = None, api_key: str | None = None):
    payload = {"email": email} if email else {}
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/magic-login",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}
