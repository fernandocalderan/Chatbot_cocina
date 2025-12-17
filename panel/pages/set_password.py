import streamlit as st

from api_client import api_set_password

st.title("Crear contraseña")
st.caption("Para continuar, crea tu contraseña de acceso.")

existing_token = st.session_state.get("token") or st.session_state.get("access_token")
if existing_token and not st.session_state.get("must_set_password"):
    st.session_state["_config_tab"] = "seguridad"
    st.switch_page("pages/configuracion.py")

if not existing_token:
    st.warning("Debes iniciar sesión con tu magic link primero.")
    st.stop()

pwd = st.text_input("Nueva contraseña", type="password")
pwd2 = st.text_input("Confirmar contraseña", type="password")
st.caption("Requisitos: 10+ caracteres, 1 mayúscula, 1 número y 1 símbolo.")

if st.button("Guardar contraseña"):
    if not pwd or not pwd2:
        st.error("Completa ambos campos.")
    else:
        with st.spinner("Guardando..."):
            resp = api_set_password(pwd, pwd2)
        if resp and resp.get("status") == "ok":
            st.session_state["must_set_password"] = False
            if resp.get("token"):
                st.session_state["token"] = resp["token"]
                st.session_state["access_token"] = resp["token"]
            st.success("Contraseña creada. Redirigiendo...")
            st.switch_page("pages/inicio.py")
