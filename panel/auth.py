import os
import streamlit as st


def ensure_login() -> str | None:
    token = st.session_state.get("token") or st.session_state.get("access_token")
    if not st.session_state.get("tenant_id") and os.getenv("PANEL_TENANT_ID"):
        # Prefill tenant_id for the session if not set yet
        st.session_state["tenant_id"] = os.getenv("PANEL_TENANT_ID")
    if token:
        return token
    # Redirige a la página de login
    try:
        st.switch_page("auth.py")
    except Exception:
        try:
            st.switch_page("pages/auth.py")
        except Exception:
            st.stop()
    st.stop()
