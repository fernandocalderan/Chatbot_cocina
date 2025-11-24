import streamlit as st

from api_client import chat_history, chat_send, fetch_flow
from auth import ensure_login
from utils import load_styles

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth")
ensure_login()

st.title("Historial de Chat")

session_id = st.text_input("Session ID", value=st.session_state.get("session_id", ""))

def render_bubbles(history: list[dict]):
    for msg in history:
        role = msg.get("role")
        content = msg.get("content") or ""
        bubble_class = "bubble-user" if role == "user" else "bubble-bot"
        align = "right" if role == "user" else "left"
        st.markdown(
            f"<div style='text-align:{align};'><div class='chat-bubble {bubble_class}'>{content}</div></div>",
            unsafe_allow_html=True,
        )

def extract_vars(history: list[dict]):
    # Busca variables en mensajes tipo system con contenido en JSON simple
    vars_found = {}
    for msg in history:
        if msg.get("role") == "system":
            try:
                # naive parse of dict-like content
                if isinstance(msg.get("content"), dict):
                    vars_found.update(msg["content"])
            except Exception:
                continue
    return vars_found

col1, col2 = st.columns(2)
if col1.button("Cargar historial") and session_id:
    st.session_state["session_id"] = session_id
    with st.spinner("Cargando historial..."):
        hist = chat_history(session_id)
    if isinstance(hist, list) and hist:
        render_bubbles(hist)
        vars_found = extract_vars(hist)
        if vars_found:
            st.subheader("Variables recogidas")
            st.json(vars_found)
    elif isinstance(hist, dict) and hist.get("detail"):
        st.error(f"Error: {hist}")
    else:
        st.info("Sin historial para esta sesión.")

st.divider()
st.subheader("Enviar mensaje de prueba")
message = st.text_input("Mensaje", "hola")
lang = st.selectbox("Idioma", ["es", "en"], index=0)

if col2.button("Enviar mensaje"):
    with st.spinner("Enviando mensaje..."):
        res = chat_send(message, session_id or None, lang)
    if res:
        st.json(res)
        st.session_state["session_id"] = res.get("session_id") or session_id
