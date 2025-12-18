import os
import streamlit as st

from api_client import login, api_magic_login, admin_issue_magic_link
from nav import nav_v2_enabled, show_flash
from utils import load_styles

load_styles()
show_flash()
st.title("Login")

# Si ya hay sesión activa, redirige al panel
existing_token = st.session_state.get("token") or st.session_state.get("access_token")
if existing_token:
    st.session_state["_config_tab"] = "seguridad"
    st.switch_page("pages/configuracion.py")

default_tenant = st.session_state.get("tenant_id") or os.getenv("PANEL_TENANT_ID", "")

mode = st.radio(
    "Método de acceso",
    options=["Email y contraseña", "Magic link"],
    horizontal=True,
    label_visibility="collapsed",
)

if mode == "Email y contraseña":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    tenant_input = st.text_input("Tenant ID", value=default_tenant)

    if st.button("Login", use_container_width=True):
        if not email or not password:
            st.error("Ingresa email y contraseña.")
        else:
            with st.spinner("Autenticando..."):
                token = login(email, password, tenant_input)
            if token:
                st.session_state["token"] = token
                st.session_state["access_token"] = token
                # `api_client.login()` ya fija `tenant_id` desde el JWT; no sobrescribirlo
                # con un valor manual (evita quedarse “enganchado” a un tenant por defecto).
                st.session_state["must_set_password"] = False
                st.session_state.pop("_api_error_shown", None)
                st.success("Autenticación correcta")
                st.switch_page("pages/inicio.py" if nav_v2_enabled() else "app.py")
            elif st.session_state.get("must_set_password_required"):
                st.info("Debes activar tu cuenta primero. Usa el enlace de magic login.")

else:
    st.caption("Pega el token del magic link para entrar o activar tu cuenta.")

    token_qp = None
    try:
        token_qp = st.query_params.get("token")
        if isinstance(token_qp, list):
            token_qp = token_qp[0] if token_qp else None
    except Exception:
        token_qp = None

    token_input = st.text_area("Token", value=str(token_qp or ""), height=120)
    if st.button("Validar magic link", use_container_width=True):
        if not token_input.strip():
            st.error("Falta el token.")
        else:
            with st.spinner("Validando..."):
                resp = api_magic_login(token_input.strip())
            if resp and isinstance(resp, dict) and resp.get("token"):
                st.session_state["token"] = resp["token"]
                st.session_state["access_token"] = resp["token"]
                st.session_state["must_set_password"] = bool(resp.get("must_set_password"))
                st.session_state.pop("_api_error_shown", None)
                st.success("Acceso válido.")
                if st.session_state.get("must_set_password"):
                    st.session_state["_config_tab"] = "seguridad"
                    st.switch_page("pages/configuracion.py")
                else:
                    st.switch_page("pages/inicio.py" if nav_v2_enabled() else "app.py")
            else:
                st.error("Magic link inválido o expirado.")

    with st.expander("No tengo un token (solo local)", expanded=False):
        st.caption("Genera un token temporal en local (si el email no llega).")
        tid = st.text_input("Tenant ID", value=default_tenant, key="ml_tenant")
        email = st.text_input("Email", value="", key="ml_email", placeholder="demo@kitchens.com")
        st.caption("Esto usa el superadmin local (si existe). En producción, el token llega por email.")
        if st.button("Generar token", use_container_width=True, key="ml_generate"):
            if not tid.strip():
                st.error("Falta Tenant ID.")
            elif not email.strip():
                st.error("Falta el email.")
            else:
                with st.spinner("Generando..."):
                    out = admin_issue_magic_link(tid.strip(), email=email.strip() or None, admin_api_token=None)
                if isinstance(out, dict) and out.get("token"):
                    st.success("Token generado.")
                    st.code(out.get("token"))
                    st.caption("Pégalo arriba en “Token” y valida.")
                else:
                    st.error("No se pudo generar el token.")
