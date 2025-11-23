import streamlit as st


def ensure_login() -> str | None:
    token = st.session_state.get("token") or st.session_state.get("access_token")
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
