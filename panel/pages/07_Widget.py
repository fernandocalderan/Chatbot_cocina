import os
import streamlit as st

from auth import ensure_login
from utils import load_styles
from api_client import issue_widget_token

load_styles()
ensure_login()

st.title("Instalación del widget")
st.write(
    "Incrusta el asistente en tu web añadiendo este snippet. El token es de corta duración "
    "(15-60 min) y se renueva automáticamente en el widget."
)

default_origin = os.getenv("WIDGET_ALLOWED_ORIGIN", "https://tu-dominio.com")
cdn_url = os.getenv("WIDGET_CDN_URL", "https://cdn.opunnence.com/widget.js")
api_base = os.getenv("API_BASE", "https://api.opunnence.com")
tenant_id = st.session_state.get("tenant_id") or os.getenv("PANEL_TENANT_ID", "<TENANT_ID>")

col1, col2 = st.columns(2)
with col1:
    allowed_origin = st.text_input("Dominio permitido", value=default_origin, help="Ej: https://opunnence.com")
with col2:
    ttl = st.slider("TTL del token (minutos)", min_value=15, max_value=60, value=30, step=5)

token_data = None
if st.button("Generar token seguro"):
    with st.spinner("Creando token..."):
        resp = issue_widget_token(allowed_origin, ttl_minutes=ttl)
    if resp and isinstance(resp, dict) and resp.get("token"):
        token_data = resp
        st.success(f"Token generado. Expira a las {resp.get('expires_at')}")
    else:
        st.error("No se pudo generar el token. Revisa el dominio permitido y tus credenciales.")

if token_data:
    snippet = f"""<div id="widget-root"></div>
<script src="{cdn_url}" async
  data-api="{api_base}"
  data-tenant="{tenant_id}"
  data-token="{token_data.get("token")}"
  data-start-open="false">
</script>"""
    st.subheader("Snippet de integración")
    st.code(snippet, language="html")
    st.info(
        "Puedes cambiar data-start-open a true para abrirlo automáticamente. "
        "El widget renovará el token antes de su expiración siempre que el dominio coincida."
    )
