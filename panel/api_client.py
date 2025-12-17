import logging
import os
import uuid
import base64
import json
from typing import Any

import requests
import streamlit as st

# API base: usa API_BASE si está, o por defecto el puerto de docker-compose (8100)
API_BASE = os.getenv("API_BASE", "http://localhost:8100").rstrip("/")
API_PREFIX = "/v1"
TENANT_ID = os.getenv("PANEL_TENANT_ID") or "3ef65ee3-b31a-4b48-874e-d8d937cb7766"
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

    def patch(self, path: str, data: dict):
        return requests.patch(self._full_url(path), json=data, headers=self.headers(), timeout=10)


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
        token = data.get("access_token")
        _maybe_set_tenant_from_token(token)
        return token
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
        data = resp.json()
        _maybe_set_tenant_from_token(data.get("token"))
        return data
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
        data = resp.json()
        _maybe_set_tenant_from_token(data.get("token"))
        return data
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
    # UX: evita exponer errores técnicos (códigos, payloads) al comercial.
    st.info(fallback_message)
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


def api_patch(path: str, payload: dict) -> Any:
    client = _client()
    resp = client.patch(path, payload)
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


def get_lead(lead_id: str):
    return api_get(f"/leads/{lead_id}") or {}


def update_lead_panel(lead_id: str, internal_note: str | None = None, quote_status: str | None = None):
    payload: dict[str, Any] = {}
    if internal_note is not None:
        payload["internal_note"] = internal_note
    if quote_status is not None:
        payload["quote_status"] = quote_status
    if not payload:
        return {"ok": True}
    return api_patch(f"/leads/{lead_id}/panel", payload) or {}


def list_appointments(lead_id: str | None = None, estado: str | None = None, fecha: str | None = None, limit: int = 200):
    qs = []
    if lead_id:
        qs.append(f"lead_id={lead_id}")
    if estado:
        qs.append(f"estado={estado}")
    if fecha:
        qs.append(f"fecha={fecha}")
    qs.append(f"limit={int(limit)}")
    path = "/appointments"
    if qs:
        path = f"{path}?{'&'.join(qs)}"
    data = api_get(path)
    if isinstance(data, dict) and "items" in data:
        return data.get("items") or []
    if isinstance(data, list):
        return data
    return []


def confirm_appointment(appt_id: str):
    return api_post("/appointments/confirm", {"id": appt_id})


def cancel_appointment(appt_id: str):
    return api_post("/appointments/cancel", {"id": appt_id})


def reschedule_appointment(appt_id: str, slot_start_iso: str):
    return api_post("/appointments/reschedule", {"id": appt_id, "slot_start": slot_start_iso})


def update_appointment(appt_id: str, payload: dict):
    return api_patch(f"/appointments/{appt_id}", payload)


def download_lead_pdf(lead_id: str, kind: str = "comercial"):
    client = _client()
    resp = client.get(f"/files/{lead_id}/{kind}.pdf")
    if resp.ok:
        return {"content": resp.content, "content_type": resp.headers.get("content-type") or "application/pdf"}
    return _handle_api_error(resp, fallback_message="Aún no hay PDF disponible para este lead.")


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


def get_tenant_config():
    return api_get("/tenant/config") or {}


def _decode_jwt_payload(token: str | None) -> dict:
    if not token or "." not in token:
        return {}
    try:
        payload_b64 = token.split(".")[1]
        padding = "=" * (-len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64 + padding)
        return json.loads(decoded)
    except Exception:
        return {}


def _maybe_set_tenant_from_token(token: str | None):
    if not token:
        return
    if not st.session_state.get("tenant_id"):
        payload = _decode_jwt_payload(token)
        tid = payload.get("tenant_id") or TENANT_ID
        if tid:
            st.session_state["tenant_id"] = tid
