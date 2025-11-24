import os
import streamlit as st

from api_client import login
from utils import load_styles

load_styles()
st.title("Login")

# Si ya hay sesión activa, redirige al panel
existing_token = st.session_state.get("token") or st.session_state.get("access_token")
if existing_token:
    st.success("Ya estás autenticado, redirigiendo…")
    st.experimental_rerun()

default_tenant = st.session_state.get("tenant_id") or os.getenv("PANEL_TENANT_ID", "")

email = st.text_input("Email")
password = st.text_input("Password", type="password")
tenant_input = st.text_input("Tenant ID", value=default_tenant)

if st.button("Login"):
    if not email or not password:
        st.error("Ingresa email y contraseña.")
    else:
        with st.spinner("Autenticando..."):
            token = login(email, password, tenant_input)
        if token:
            st.session_state["token"] = token
            st.session_state["access_token"] = token  # compat con cliente existente
            st.session_state["tenant_id"] = tenant_input
            st.success("Autenticación correcta")
            st.switch_page("app.py")
