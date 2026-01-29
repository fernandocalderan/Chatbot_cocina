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


def get_catalog(
    token: str | None,
    *,
    vertical_key: str | None = None,
    tenant_id: str | None = None,
    include_empty_scopes: bool = True,
    include_drafts: bool = True,
    include_templates: bool = True,
    only_published: bool = False,
    api_key: str | None = None,
):
    params: dict[str, object] = {
        "include_empty_scopes": include_empty_scopes,
        "include_drafts": include_drafts,
        "include_templates": include_templates,
        "only_published": only_published,
    }
    if vertical_key:
        params["vertical_key"] = vertical_key
    if tenant_id:
        params["tenant_id"] = tenant_id
    resp = requests.get(
        f"{API_BASE}/v1/catalog",
        headers=_headers(token, api_key or _admin_api_key()),
        params=params,
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def create_scope(
    token: str | None,
    *,
    vertical_key: str,
    scope_key: str,
    display_name: str,
    description: str | None = None,
    api_key: str | None = None,
):
    payload = {
        "vertical_key": vertical_key,
        "scope_key": scope_key,
        "display_name": display_name,
        "description": description,
    }
    resp = requests.post(
        f"{API_BASE}/v1/scopes",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def import_flow_base(
    token: str | None,
    *,
    file_name: str,
    file_bytes: bytes,
    vertical_key: str,
    scope_key: str,
    owner_type: str = "TENANT",
    owner_id: str | None = None,
    api_key: str | None = None,
):
    data = {
        "vertical_key": vertical_key,
        "scope_key": scope_key,
        "flow_kind": "base",
        "owner_type": owner_type,
    }
    if owner_id:
        data["owner_id"] = owner_id
    files = {
        "file": (file_name, file_bytes, "application/json"),
    }
    resp = requests.post(
        f"{API_BASE}/v1/flows/import",
        headers=_headers(token, api_key or _admin_api_key()),
        data=data,
        files=files,
        timeout=30,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def publish_flow_by_id(token: str | None, flow_id: str, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/flows/{flow_id}/publish",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def flatten_catalog_scopes(catalog_json: dict) -> list[dict]:
    rows: list[dict] = []
    for v in catalog_json.get("verticals") or []:
        vkey = v.get("vertical_key")
        for s in v.get("scopes") or []:
            flows = s.get("flows") or []
            published_count = len([f for f in flows if f.get("published")])
            rows.append(
                {
                    "vertical_key": vkey,
                    "scope_key": s.get("scope_key"),
                    "status": s.get("status"),
                    "flows_count": len(flows),
                    "published_count": published_count,
                    "has_fs_def": bool(s.get("has_filesystem_definition")),
                    "source": s.get("source"),
                }
            )
    return rows


def flatten_catalog_flows(catalog_json: dict) -> list[dict]:
    rows: list[dict] = []
    for v in catalog_json.get("verticals") or []:
        vkey = v.get("vertical_key")
        for s in v.get("scopes") or []:
            skey = s.get("scope_key")
            for f in s.get("flows") or []:
                rows.append(
                    {
                        "vertical_key": vkey,
                        "scope_key": skey,
                        "flow_id": f.get("flow_id"),
                        "name": f.get("name"),
                        "version": f.get("version"),
                        "published": bool(f.get("published")),
                        "published_at": f.get("published_at"),
                        "owner_type": f.get("owner_type"),
                        "owner_id": f.get("owner_id"),
                    }
                )
    return rows


def get_vertical(token: str | None, vertical_key: str, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=10,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def create_vertical_admin(token: str | None, payload: dict, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/verticals",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def update_vertical_file_admin(
    token: str | None,
    vertical_key: str,
    filename: str,
    *,
    kind: str,
    content,
    validate: bool = True,
    api_key: str | None = None,
):
    resp = requests.put(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}/files/{filename}",
        json={"kind": kind, "content": content, "validate": validate},
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=30,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def list_vertical_files_admin(token: str | None, vertical_key: str, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}/files",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    return resp.json() if resp.ok else {"items": [], "error": resp.text, "status_code": resp.status_code}


def read_vertical_file_admin(
    token: str | None,
    vertical_key: str,
    filename: str,
    *,
    api_key: str | None = None,
):
    resp = requests.get(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}/files/{filename}",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def delete_vertical_file_admin(token: str | None, vertical_key: str, filename: str, api_key: str | None = None):
    resp = requests.delete(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}/files/{filename}",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=30,
    )
    return resp.json() if resp.ok else {"error": resp.text, "status_code": resp.status_code}


def preview_vertical_flow_generator(
    token: str | None,
    vertical_key: str,
    payload: dict,
    *,
    api_key: str | None = None,
):
    resp = requests.post(
        f"{API_BASE}/v1/admin/verticals/{vertical_key}/flow-generator/preview",
        json=payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=60,
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


def include_tenant(token: str | None, tenant_id: str, reason: str | None = None, api_key: str | None = None):
    payload = {"reason": reason} if reason else {}
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/include",
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


def get_tenant_flow(token: str | None, tenant_id: str, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/flow",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def get_published_flow(token: str | None, tenant_id: str, api_key: str | None = None):
    resp = requests.get(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/flow",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    if resp.ok:
        data = resp.json()
        published = data.get("published") if isinstance(data, dict) else None
        return {"status": "OK", "flow": published or {}, "raw": data}
    if resp.status_code == 409:
        detail = ""
        try:
            detail = str((resp.json() or {}).get("detail") or "")
        except Exception:
            detail = resp.text or ""
        detail_lower = detail.lower()
        if "multiple" in detail_lower:
            return {"status": "MULTIPLE_PUBLISHED", "flow": None, "error": detail, "status_code": resp.status_code}
        if "no_published" in detail_lower or "no published" in detail_lower:
            return {"status": "NO_PUBLISHED", "flow": None, "error": detail, "status_code": resp.status_code}
        return {"status": "ERROR", "flow": None, "error": detail, "status_code": resp.status_code}
    return {"status": "ERROR", "flow": None, "error": resp.text, "status_code": resp.status_code}


def publish_tenant_flow(token: str | None, tenant_id: str, flow_payload: dict, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/flow",
        json=flow_payload,
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=30,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def publish_flow(token: str | None, tenant_id: str, flow_payload: dict, api_key: str | None = None):
    return publish_tenant_flow(token, tenant_id, flow_payload, api_key=api_key)


def reset_tenant_flow(token: str | None, tenant_id: str, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/flow/reset",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def reset_sessions(token: str | None, tenant_id: str, api_key: str | None = None):
    resp = requests.post(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/sessions/reset",
        headers=_headers(token, api_key or _admin_api_key()),
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"error": resp.text, "status_code": resp.status_code}


def list_tenant_flow_versions(
    token: str | None,
    tenant_id: str,
    *,
    limit: int = 20,
    include_schema: bool = False,
    api_key: str | None = None,
):
    resp = requests.get(
        f"{API_BASE}/v1/admin/tenants/{tenant_id}/flow/versions",
        headers=_headers(token, api_key or _admin_api_key()),
        params={"limit": limit, "include_schema": include_schema},
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"items": [], "error": resp.text, "status_code": resp.status_code}


def list_flows(
    token: str | None,
    tenant_id: str,
    *,
    limit: int = 20,
    include_schema: bool = False,
    api_key: str | None = None,
):
    return list_tenant_flow_versions(
        token,
        tenant_id,
        limit=limit,
        include_schema=include_schema,
        api_key=api_key,
    )


def admin_audits_recent(
    token: str | None,
    *,
    tenant_id: str | None = None,
    action_prefix: str | None = None,
    actor: str | None = None,
    limit: int = 50,
    api_key: str | None = None,
):
    params: dict[str, object] = {"limit": limit}
    if tenant_id:
        params["tenant_id"] = tenant_id
    if action_prefix:
        params["action_prefix"] = action_prefix
    if actor:
        params["actor"] = actor
    resp = requests.get(
        f"{API_BASE}/v1/admin/audits/recent",
        headers=_headers(token, api_key or _admin_api_key()),
        params=params,
        timeout=20,
    )
    if resp.ok:
        return resp.json()
    return {"items": [], "error": resp.text, "status_code": resp.status_code}
