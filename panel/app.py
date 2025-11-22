import json
import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:9000")
AUTH_HEADER = {}
# Puedes setear TOKEN en env si lo necesitas: AUTH_HEADER = {"Authorization": f"Bearer {TOKEN}"}


def api_get(path: str):
    resp = requests.get(f"{API_BASE}{path}", headers=AUTH_HEADER, timeout=10)
    if resp.ok:
        return resp.json()
    st.error(resp.text)
    return None


def api_post(path: str, payload: dict):
    resp = requests.post(f"{API_BASE}{path}", json=payload, headers=AUTH_HEADER, timeout=10)
    if resp.ok:
        return resp.json()
    st.error(resp.text)
    return None


def fetch_flow(tenant_id: str = "demo"):
    return api_get(f"/flows/{tenant_id}")


def chat_send(message: str, session_id: str | None = None, lang: str = "es"):
    payload = {"message": message, "lang": lang}
    if session_id:
        payload["session_id"] = session_id
    return api_post("/chat/send", payload)


def chat_history(session_id: str):
    return api_get(f"/chat/history/{session_id}") or []


def list_leads():
    return api_get("/leads") or []


def list_appointments():
    return api_get("/appointments/slots") or []


def load_scoring_from_flow():
    flow = fetch_flow("demo")
    if flow and "flow" in flow:
        return flow["flow"].get("scoring", {})
    return {}


st.set_page_config(page_title="Panel Demo", layout="wide")
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Chat", "Leads", "Citas", "Scoring", "Flujos"])

# Chat Page
if page == "Chat":
    st.title("Chat de prueba")
    tenant = st.text_input("Tenant", "demo")
    lang = st.selectbox("Idioma", ["es", "ca", "pt", "en"], index=0)
    session_state = st.session_state.setdefault("session_id", None)
    msg = st.text_input("Mensaje al bot", "hola")

    flow_cached = st.session_state.get("flow_cache") or fetch_flow(tenant)
    label_to_id = {}
    if flow_cached and "flow" in flow_cached:
        blocks = flow_cached["flow"].get("blocks", {})
        for b in blocks.values():
            for opt in b.get("options", []):
                label_to_id[opt.get("label_es", "")] = opt["id"]

    col_btn = st.columns(3)
    if col_btn[0].button("Enviar"):
        payload_text = label_to_id.get(msg, msg)
        res = chat_send(payload_text, session_state, lang)
        if res:
            st.session_state["session_id"] = res.get("session_id")
            st.json(res)
    if col_btn[1].button("Ver historial") and session_state:
        hist = chat_history(session_state)
        st.json(hist)
    if col_btn[2].button("Cargar flujo"):
        flow = fetch_flow(tenant)
        st.session_state["flow_cache"] = flow
        st.json(flow)

# Leads Page
elif page == "Leads":
    st.title("Leads")
    leads = list_leads()
    if leads:
        st.dataframe(
            [
                {
                    "id": l["id"],
                    "score": l.get("score"),
                    "status": l.get("status"),
                    "created_at": l.get("created_at"),
                    "project_type": (l.get("metadata") or {}).get("project_type"),
                    "phone": (l.get("metadata") or {}).get("contact_phone"),
                    "name": (l.get("metadata") or {}).get("contact_name"),
                }
                for l in leads
            ]
        )
        sel = st.selectbox("Selecciona lead", [l["id"] for l in leads])
        if st.button("Ver historial", key="hist_lead"):
            lead = next((x for x in leads if x["id"] == sel), None)
            if lead and lead.get("session_id"):
                st.json(chat_history(lead["session_id"]))
        if st.button("Ver citas", key="appt_lead"):
            st.info("Conectar a /appointments cuando expongamos listado; ahora slots fijos en /appointments/slots.")

# Citas Page (stub lista slots)
elif page == "Citas":
    st.title("Citas")
    slots = api_get("/appointments/slots") or {}
    st.json(slots)
    st.info("Cambiar status requeriría un endpoint PATCH; pendiente de implementar.")

# Scoring Page
elif page == "Scoring":
    st.title("Scoring")
    scoring = st.session_state.setdefault("scoring_cfg", load_scoring_from_flow())
    weights = scoring.get("weights", {})
    st.subheader("Pesos")
    for key in ["budget", "urgency", "area_m2", "style_defined", "origin"]:
        weights[key] = st.number_input(f"Peso {key}", value=float(weights.get(key, 0)), step=5.0)
    scoring["weights"] = weights
    if st.button("Guardar scoring"):
        # Stub: debería persistir en configs; ahora solo se queda en sesión.
        st.session_state["scoring_cfg"] = scoring
        st.success("Scoring actualizado en sesión (persistencia pendiente en configs).")

# Flujos Page
elif page == "Flujos":
    st.title("Flujos")
    flow = fetch_flow("demo")
    if flow and "flow" in flow:
        st.json(flow["flow"])
    else:
        st.json(flow)
