import os
import streamlit as st


def ensure_login() -> str | None:
    token = st.session_state.get("token") or st.session_state.get("access_token")
    if st.session_state.get("must_set_password"):
        try:
            st.switch_page("pages/set_password.py")
        except Exception:
            st.stop()
    default_tid = os.getenv("PANEL_TENANT_ID") or "3ef65ee3-b31a-4b48-874e-d8d937cb7766"
    if token and not st.session_state.get("tenant_id"):
        st.session_state["tenant_id"] = default_tid
    if not st.session_state.get("tenant_id"):
        # Prefill tenant_id for the session if not set yet
        st.session_state["tenant_id"] = default_tid
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
