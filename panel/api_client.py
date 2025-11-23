import os
from typing import Any

import requests
import streamlit as st

# API base: usa API_BASE si está, o por defecto el puerto de docker-compose (8100)
API_BASE = os.getenv("API_BASE", "http://localhost:8100").rstrip("/")


class API:
    def __init__(self, api_url: str, token: str | None):
        self.api_url = api_url.rstrip("/")
        self.token = token

    def headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, path: str):
        return requests.get(self.api_url + path, headers=self.headers(), timeout=10)

    def post(self, path: str, data: dict):
        return requests.post(self.api_url + path, json=data, headers=self.headers(), timeout=10)


def _client() -> API:
    token = st.session_state.get("token") or st.session_state.get("access_token")
    return API(API_BASE, token)


def api_login(email: str, password: str) -> str | None:
    try:
        resp = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password}, timeout=10)
    except requests.RequestException as exc:
        st.error(f"Error de red al autenticar: {exc}")
        return None
    if resp.ok:
        data = resp.json()
        return data.get("access_token")
    st.error(f"Login inválido: {resp.text}")
    return None


def api_get(path: str) -> Any:
    client = _client()
    try:
        resp = client.get(path)
    except requests.RequestException as exc:
        st.error(f"Error de red: {exc}")
        return None
    if resp.ok:
        return resp.json()
    st.error(f"Error {resp.status_code}: {resp.text}")
    return None


def api_post(path: str, payload: dict) -> Any:
    client = _client()
    try:
        resp = client.post(path, payload)
    except requests.RequestException as exc:
        st.error(f"Error de red: {exc}")
        return None
    if resp.ok:
        return resp.json()
    st.error(f"Error {resp.status_code}: {resp.text}")
    return None


def fetch_flow():
    return api_get("/flows/current")


def chat_send(message: str, session_id: str | None = None, lang: str = "es"):
    payload: dict[str, Any] = {"message": message, "lang": lang}
    if session_id:
        payload["session_id"] = session_id
    return api_post("/chat/send", payload)


def chat_history(session_id: str):
    return api_get(f"/chat/history/{session_id}") or []


def list_leads():
    return api_get("/leads") or []


def list_appointments():
    return api_get("/appointments") or []


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


def login(email: str, password: str) -> str | None:
    return api_login(email, password)


def load_scoring_from_flow():
    flow = fetch_flow("demo")
    if flow and "flow" in flow:
        return flow["flow"].get("scoring", {})
    return {}
