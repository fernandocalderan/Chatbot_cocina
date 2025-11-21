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


st.set_page_config(page_title="Panel Demo", layout="wide")
st.title("Panel Demo - Chatbot Cocinas")

cols = st.columns(2)
with cols[0]:
    st.subheader("Flujo")
    tenant = st.text_input("Tenant", "demo")
    if st.button("Cargar flujo"):
        flow = fetch_flow(tenant)
        st.json(flow)

with cols[1]:
    st.subheader("Chat de prueba")
    session_state = st.session_state.setdefault("session_id", None)
    msg = st.text_input("Mensaje al bot", "hola")
    if st.button("Enviar"):
        res = chat_send(msg, session_state)
        st.session_state["session_id"] = res.get("session_id")
        st.json(res)
