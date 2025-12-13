import streamlit as st

from api_client import get_billing
from auth import ensure_login
from utils import load_styles, render_quota_banner

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth")
ensure_login()

st.title("Facturación")

with st.spinner("Cargando facturación..."):
    billing = get_billing()

if not isinstance(billing, dict) or not billing:
    st.error("No se pudo obtener el estado de facturación.")
    st.stop()

plan = billing.get("plan") or "N/D"
status = billing.get("billing_status") or billing.get("stripe_status") or "N/D"
renewal = billing.get("current_period_end")
limits = billing.get("limits") or {}
quota_status = billing.get("quota_status")
needs_upgrade = False
if isinstance(quota_status, dict):
    needs_upgrade = bool(quota_status.get("needs_upgrade_notice"))
render_quota_banner(quota_status, needs_upgrade=needs_upgrade, upgrade_url=billing.get("manage_url"))

cols = st.columns(3)
cols[0].metric("Plan", plan)
cols[1].metric("Estado", status)
cols[2].metric("Renovación", renewal or "N/D")

st.subheader("Límites del plan")
st.json(limits)

portal = billing.get("manage_url")
if portal:
    st.success("Gestiona tu suscripción en el portal de Stripe.")
    st.markdown(f"[Abrir portal de facturación]({portal})")
else:
    st.info("Portal de facturación no disponible. Asegúrate de tener cliente Stripe asignado.")
