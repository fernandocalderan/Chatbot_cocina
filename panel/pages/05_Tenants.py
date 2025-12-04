import streamlit as st

from api_client import api_post

st.set_page_config(page_title="Tenants", page_icon="🏢", layout="wide")

st.title("Gestión de Tenants")
st.caption("Crea nuevos tenants desde el panel de superadmin.")

role = st.session_state.get("role")
if role != "SUPER_ADMIN":
    st.error("Acceso restringido: solo SUPER_ADMIN puede crear tenants.")
    st.stop()

with st.form("create_tenant"):
    name = st.text_input("Nombre del tenant", "")
    contact_email = st.text_input("Email de contacto", "")
    plan = st.selectbox("Plan", ["BASE", "PRO", "ELITE"], index=0)
    timezone = st.text_input("Zona horaria", "Europe/Madrid")
    idioma = st.text_input("Idioma por defecto", "es")
    submitted = st.form_submit_button("Crear tenant")

    if submitted:
        if not name.strip():
            st.error("El nombre es obligatorio.")
        else:
            payload = {
                "name": name.strip(),
                "contact_email": contact_email.strip() or None,
                "plan": plan,
                "timezone": timezone.strip() or "Europe/Madrid",
                "idioma_default": idioma.strip() or "es",
            }
            with st.spinner("Creando tenant..."):
                res = api_post("/tenants", payload)
            if isinstance(res, dict) and res.get("id"):
                st.success(f"Tenant creado: {res['name']} (ID: {res['id']})")
            else:
                st.error("No se pudo crear el tenant.")
