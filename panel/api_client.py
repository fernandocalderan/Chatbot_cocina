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
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN") or os.getenv("ADMIN_API_KEY")
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

    def put(self, path: str, data: dict):
        return requests.put(self._full_url(path), json=data, headers=self.headers(), timeout=10)


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


def _load_local_admin_api_token() -> str | None:
    """
    Conveniencia para entorno local:
    - Si no hay ADMIN_API_TOKEN en env, intenta leerlo desde ../backend/.env.
    - Solo aplica cuando API_BASE apunta a localhost/127.0.0.1.
    """
    if ADMIN_API_TOKEN:
        return ADMIN_API_TOKEN
    if "localhost" not in API_BASE and "127.0.0.1" not in API_BASE:
        return None
    try:
        here = os.path.dirname(__file__)
        env_path = os.path.abspath(os.path.join(here, "..", "backend", ".env"))
        if not os.path.exists(env_path):
            return None
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("ADMIN_API_TOKEN="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        return None
    return None


def admin_issue_magic_link(tenant_id: str, email: str | None = None, admin_api_token: str | None = None):
    key = (admin_api_token or _load_local_admin_api_token() or "").strip()
    if not key:
        return {"status_code": 401, "detail": "missing_admin_api_token"}
    payload: dict[str, Any] = {}
    if email:
        payload["email"] = email
    try:
        resp = requests.post(
            f"{API_BASE}{API_PREFIX}/admin/tenants/{tenant_id}/magic-login",
            json=payload,
            headers={"x-api-key": key},
            timeout=10,
        )
    except requests.RequestException as exc:
        st.info("No se pudo completar la operación con la API.")
        logger.error("Admin magic link request failed: %s", exc)
        return {"status_code": 0, "detail": str(exc)}
    if resp.ok:
        return resp.json()
    return _handle_api_error(resp, fallback_message="No se pudo generar el magic link.")


def _handle_api_error(resp: requests.Response, fallback_message: str = "No se pudo completar la operación con la API."):
    try:
        detail = resp.json()
    except Exception:
        detail = resp.text
    status = resp.status_code
    url = getattr(resp.request, "url", "") if getattr(resp, "request", None) else ""

    # Caso especial: el backend bloquea por activación pendiente.
    detail_str = ""
    if isinstance(detail, dict):
        detail_str = str(detail.get("detail") or "")
    else:
        detail_str = str(detail or "")

    # Si el token ya no es válido, forzar re-login sin ensuciar la UI.
    if status == 401 and "/auth/" not in url:
        for k in [
            "token",
            "access_token",
            "must_set_password",
            "must_set_password_required",
            "tenant_id",
            "_branding_loaded",
            "tenant_name",
            "tenant_language",
            "tenant_logo_url",
            "tenant_timezone",
            "tenant_currency",
            "customer_code",
        ]:
            st.session_state.pop(k, None)
        st.session_state["_flash_message"] = "Necesitas iniciar sesión para continuar."
        try:
            st.switch_page("pages/auth.py")
        except Exception:
            pass
        return {"detail": detail, "status_code": status}

    # UX: evita banners repetidos.
    if not st.session_state.get("_api_error_shown"):
        if not (status == 403 and detail_str == "must_set_password_first"):
            st.info(fallback_message)
        st.session_state["_api_error_shown"] = True
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


def api_put(path: str, payload: dict) -> Any:
    client = _client()
    resp = client.put(path, payload)
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


def update_tenant_config(language: str | None = None, timezone: str | None = None, currency: str | None = None):
    payload: dict[str, Any] = {}
    if language is not None:
        payload["language"] = language
    if timezone is not None:
        payload["timezone"] = timezone
    if currency is not None:
        payload["currency"] = currency
    if not payload:
        return get_tenant_config()
    return api_patch("/tenant/config", payload) or {}


def get_widget_settings():
    return api_get("/tenant/widget/settings") or {}


def update_widget_settings(allowed_origins: list[str]):
    return api_patch("/tenant/widget/settings", {"allowed_origins": allowed_origins}) or {}


def get_automation_materials():
    return api_get("/tenant/automation/materials") or {}


def save_automation_materials(payload: dict):
    return api_put("/tenant/automation/materials", payload) or {}


def publish_automation_materials():
    return api_post("/tenant/automation/materials/publish", {}) or {}


def rollback_automation_materials(version: int):
    return api_post("/tenant/automation/materials/rollback", {"version": version}) or {}


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
    payload = _decode_jwt_payload(token)
    tid = payload.get("tenant_id") or TENANT_ID
    if not tid:
        return
    prev = st.session_state.get("tenant_id")
    st.session_state["tenant_id"] = tid
    if prev and str(prev) != str(tid):
        for k in [
            "_branding_loaded",
            "tenant_name",
            "tenant_language",
            "tenant_logo_url",
            "tenant_timezone",
            "tenant_currency",
            "customer_code",
        ]:
            st.session_state.pop(k, None)
