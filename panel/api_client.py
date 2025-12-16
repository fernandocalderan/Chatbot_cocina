import logging
import os
import uuid
from typing import Any

import requests
import streamlit as st

# API base: usa API_BASE si está, o por defecto el puerto de docker-compose (8100)
API_BASE = os.getenv("API_BASE", "http://localhost:8100").rstrip("/")
API_PREFIX = "/v1"
TENANT_ID = os.getenv("PANEL_TENANT_ID")
API_TOKEN = os.getenv("PANEL_API_TOKEN")
logger = logging.getLogger(__name__)


class API:
    def __init__(self, api_url: str, token: str | None):
        self.api_url = api_url.rstrip("/")
        self.token = token

    def _full_url(self, path: str) -> str:
        return f"{self.api_url}{API_PREFIX}{path}"

    def headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif API_TOKEN:
            headers["x-api-key"] = API_TOKEN
            headers["Authorization"] = f"Bearer {API_TOKEN}"
        tenant = _current_tenant_id()
        if tenant:
            headers["X-Tenant-ID"] = tenant
        return headers

    def get(self, path: str):
        return requests.get(self._full_url(path), headers=self.headers(), timeout=10)

    def post(self, path: str, data: dict, idempotency_key: str | None = None):
        headers = self.headers()
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return requests.post(self._full_url(path), json=data, headers=headers, timeout=10)


def _current_tenant_id() -> str | None:
    return st.session_state.get("tenant_id") or TENANT_ID


def _client() -> API:
    token = st.session_state.get("token") or st.session_state.get("access_token")
    return API(API_BASE, token)


def api_login(email: str, password: str, tenant_id: str | None = None) -> str | None:
    try:
        tenant_header = tenant_id or _current_tenant_id() or ""
        resp = requests.post(
            f"{API_BASE}{API_PREFIX}/auth/login",
            json={"email": email, "password": password},
            headers={"X-Tenant-ID": tenant_header, **({"x-api-key": API_TOKEN, "Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {})},
            timeout=10,
        )
    except requests.RequestException as exc:
        st.error(f"Error de red al autenticar: {exc}")
        return None

    if resp.ok:
        data = resp.json()
        return data.get("access_token")
    try:
        detail = resp.json().get("detail")
    except Exception:
        detail = None
    if resp.status_code == 403 and detail == "must_set_password_first":
        st.session_state["must_set_password_required"] = True
        st.warning("Debes activar tu cuenta primero con el magic link.")
        return None

    _handle_api_error(resp, fallback_message="No se pudo iniciar sesión.")
    return None


def api_magic_login(token: str):
    try:
        resp = requests.get(f"{API_BASE}{API_PREFIX}/auth/magic-login", params={"token": token}, timeout=10)
    except requests.RequestException as exc:
        st.error(f"Error de red en magic login: {exc}")
        return None
    if resp.ok:
        return resp.json()
    _handle_api_error(resp, fallback_message="Magic link inválido o expirado.")
    return None


def api_set_password(password: str, password_confirm: str):
    token = st.session_state.get("token") or st.session_state.get("access_token")
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        resp = requests.post(
            f"{API_BASE}{API_PREFIX}/auth/set-password",
            json={"password": password, "password_confirm": password_confirm},
            headers=headers,
            timeout=10,
        )
    except requests.RequestException as exc:
        st.error(f"Error de red al fijar contraseña: {exc}")
        return None
    if resp.ok:
        return resp.json()
    try:
        detail = resp.json().get("detail")
        if detail:
            st.error(f"No se pudo guardar la contraseña: {detail} (código {resp.status_code}).")
            return None
    except Exception:
        pass
    _handle_api_error(resp, fallback_message="No se pudo guardar la contraseña.")
    return None


def _handle_api_error(resp: requests.Response, fallback_message: str = "No se pudo completar la operación con la API."):
    try:
        detail = resp.json()
    except Exception:
        detail = resp.text
    status = resp.status_code
    st.error(f"{fallback_message} (código {status}).")
    logger.error("API error %s %s: %s", status, getattr(resp.request, "url", "<sin_url>"), detail)
    return {"detail": detail, "status_code": status}


def api_get(path: str) -> Any:
    client = _client()
    resp = client.get(path)
    if resp.ok:
        return resp.json()
    return _handle_api_error(resp)


def api_post(path: str, payload: dict, idempotency_key: str | None = None) -> Any:
    client = _client()
    resp = client.post(path, payload, idempotency_key=idempotency_key)
    if resp.ok:
        return resp.json()
    return _handle_api_error(resp)


def fetch_flow():
    return api_get("/flows/current")


def chat_send(message: str, session_id: str | None = None, lang: str = "es"):
    payload: dict[str, Any] = {"message": message, "lang": lang}
    if session_id:
        payload["session_id"] = session_id
    idemp_key = f"{session_id or 'no-session'}-{uuid.uuid4()}"
    return api_post("/chat/send", payload, idempotency_key=idemp_key)


def chat_history(session_id: str):
    return api_get(f"/chat/history/{session_id}") or []


def list_leads():
    data = api_get("/leads")
    if isinstance(data, dict) and "items" in data:
        return data.get("items") or []
    if isinstance(data, list):
        return data
    return []


def list_appointments():
    data = api_get("/appointments")
    if isinstance(data, dict) and "items" in data:
        return data.get("items") or []
    if isinstance(data, list):
        return data
    return []


def confirm_appointment(appt_id: str):
    return api_post("/appointments/confirm", {"id": appt_id})


def cancel_appointment(appt_id: str):
    return api_post("/appointments/cancel", {"id": appt_id})


def get_scoring():
    return api_get("/flows/scoring") or {}


def update_scoring(payload: dict):
    return api_post("/scoring/update", payload)


def update_flow(payload: dict):
    return api_post("/flows/update", payload)


def login(email: str, password: str, tenant_id: str | None = None) -> str | None:
    return api_login(email, password, tenant_id)


def load_scoring_from_flow():
    flow = fetch_flow("demo")
    if flow and "flow" in flow:
        return flow["flow"].get("scoring", {})
    return {}


def get_billing():
    return api_get("/tenant/me/billing") or {}


def issue_widget_token(allowed_origin: str, ttl_minutes: int = 30):
    return api_post("/tenant/widget/token", {"allowed_origin": allowed_origin, "ttl_minutes": ttl_minutes})


def get_quota_status():
    return api_get("/metrics/quota") or {}


def get_tenant_kpis():
    return api_get("/metrics/kpis") or {}


def count_leads(status: str | None = None) -> int:
    params = ""
    if status:
        params = f"?status={status}"
    data = api_get(f"/leads{params}")
    if isinstance(data, dict):
        return int(data.get("total", 0) or 0)
    return 0


def count_appointments(status: str | None = None) -> int:
    params = ""
    if status:
        params = f"?estado={status}"
    data = api_get(f"/appointments{params}")
    if isinstance(data, dict):
        return int(data.get("total", 0) or 0)
    return 0


def get_ia_metrics(tenant_id: str):
    return api_get(f"/metrics/ia/tenant/{tenant_id}") or {}
