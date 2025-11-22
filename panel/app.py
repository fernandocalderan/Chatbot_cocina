import os
import streamlit as st
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:9000")


def fetch_flow(tenant_id: str = "demo"):
    resp = requests.get(f"{API_BASE}/flows/{tenant_id}", timeout=5)
    if resp.ok:
        return resp.json()
    return {"error": resp.text}


def chat_send(message: str, session_id: str | None = None):
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    resp = requests.post(f"{API_BASE}/chat/send", json=payload, timeout=5)
    return resp.json()


def chat_history(session_id: str):
    resp = requests.get(f"{API_BASE}/chat/history/{session_id}", timeout=5)
    if resp.ok:
        return resp.json()
    return []


st.set_page_config(page_title="Panel Demo", layout="wide")
st.title("Panel Demo - Chatbot Cocinas")

cols = st.columns(2)
with cols[0]:
    st.subheader("Flujo")
    tenant = st.text_input("Tenant", "demo")
    lang = st.selectbox("Idioma", ["es", "ca", "pt", "en"], index=0)
    flow_state = st.session_state.setdefault("flow_cache", None)
    if st.button("Cargar flujo"):
        flow = fetch_flow(tenant)
        st.session_state["flow_cache"] = flow
        st.json(flow)

with cols[1]:
    st.subheader("Chat de prueba")
    session_state = st.session_state.setdefault("session_id", None)
    msg = st.text_input("Mensaje al bot", "hola")

    # Map labels->ids si el flow está cargado y el bloque actual es options
    flow_cached = st.session_state.get("flow_cache") or fetch_flow(tenant)
    label_to_id = {}
    if "flow" in flow_cached:
        blocks = flow_cached["flow"].get("blocks", {})
        # Intentar usar el bloque actual si hay session guardada
        if session_state and st.button("Ver historial"):
            history = chat_history(session_state)
            st.json(history)
        # Construir mapping simple para consent/ask_type etc (solo labels ES)
        for b in blocks.values():
            for opt in b.get("options", []):
                label_to_id[opt.get("label_es", "")] = opt["id"]

    if st.button("Enviar"):
        payload_text = msg
        if msg in label_to_id:
            payload_text = label_to_id[msg]
        res = chat_send(payload_text, session_state)
        st.session_state["session_id"] = res.get("session_id")
        st.json(res)
