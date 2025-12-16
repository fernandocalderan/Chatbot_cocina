import streamlit as st

from api_client import api_magic_login

st.title("Acceso con magic link")
params = st.query_params if hasattr(st, "query_params") else st.experimental_get_query_params()
token = params.get("token")
if isinstance(token, list):
    token = token[0]

token_input = st.text_input("Token", value=token or "")

if st.button("Validar link"):
    if not token_input:
        st.error("Falta el token.")
    else:
        with st.spinner("Validando..."):
            resp = api_magic_login(token_input)
        if resp and resp.get("token"):
            st.session_state["token"] = resp["token"]
            st.session_state["access_token"] = resp["token"]
            st.session_state["must_set_password"] = bool(resp.get("must_set_password"))
            st.success("Acceso válido.")
            if st.session_state.get("must_set_password"):
                st.switch_page("pages/set_password.py")
            else:
                st.switch_page("app.py")
