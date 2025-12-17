import os
import streamlit as st

from api_client import get_tenant_config


def ensure_login(*, allow_when_must_set_password: bool = False) -> str | None:
    token = st.session_state.get("token") or st.session_state.get("access_token")
    if st.session_state.get("must_set_password") and not allow_when_must_set_password:
        # Bloquea navegación normal hasta activar la cuenta.
        # Única excepción: Configuración → Seguridad y accesos.
        st.session_state["_config_tab"] = "seguridad"
        try:
            st.switch_page("pages/configuracion.py")
        except Exception:
            try:
                st.switch_page("pages/set_password.py")
            except Exception:
                st.stop()
        st.stop()
    default_tid = os.getenv("PANEL_TENANT_ID") or "3ef65ee3-b31a-4b48-874e-d8d937cb7766"
    if token and not st.session_state.get("tenant_id"):
        st.session_state["tenant_id"] = default_tid
    if not st.session_state.get("tenant_id"):
        # Prefill tenant_id for the session if not set yet
        st.session_state["tenant_id"] = default_tid
    if token:
        # Hidrata branding/config del tenant 1 vez por sesión (idioma, tz, moneda, nombre).
        if not st.session_state.get("_branding_loaded"):
            try:
                cfg = get_tenant_config() or {}
            except Exception:
                cfg = {}
            if isinstance(cfg, dict) and not cfg.get("status_code"):
                st.session_state["tenant_name"] = cfg.get("name") or st.session_state.get("tenant_name", "Tu negocio")
                st.session_state["tenant_language"] = cfg.get("language") or st.session_state.get("tenant_language", "es")
                st.session_state["tenant_logo_url"] = cfg.get("logo_url") or st.session_state.get("tenant_logo_url")
                st.session_state["tenant_timezone"] = cfg.get("timezone") or st.session_state.get("tenant_timezone", "Europe/Madrid")
                st.session_state["tenant_currency"] = cfg.get("currency") or st.session_state.get("tenant_currency", "EUR")
                st.session_state["customer_code"] = cfg.get("customer_code") or st.session_state.get("customer_code")
            st.session_state["_branding_loaded"] = True
        return token
    # Redirige a la página de login
    try:
        st.switch_page("pages/auth.py")
    except Exception:
        st.stop()
    st.stop()
