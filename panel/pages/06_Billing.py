import streamlit as st

from api_client import get_billing
from auth import ensure_login
from utils import (
    load_styles,
    render_quota_banner,
    render_quota_usage_bar,
    metric_card,
    pill,
)

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth")
ensure_login()

st.title("Facturación y plan")
st.caption("Estado del plan, consumo de IA y acciones de upgrade.")

with st.spinner("Cargando facturación..."):
    billing = get_billing()

if not isinstance(billing, dict) or not billing:
    st.error("No se pudo obtener el estado de facturación.")
    st.stop()

plan = (billing.get("plan") or "N/D").upper()
status = (billing.get("billing_status") or billing.get("stripe_status") or "N/D").upper()
renewal = billing.get("current_period_end") or "N/D"
limits = billing.get("limits") or {}
quota_status = billing.get("quota_status")
needs_upgrade = False
if isinstance(quota_status, dict):
    needs_upgrade = bool(quota_status.get("needs_upgrade_notice"))

# Banners de estado de cuota
render_quota_banner(quota_status, needs_upgrade=needs_upgrade, upgrade_url=billing.get("manage_url"))
render_quota_usage_bar(quota_status, label="Consumo IA mensual")

# Resumen en cards
col_top = st.columns(3)
with col_top[0]:
    metric_card("Plan", plan, subtitle="Nivel actual", accent="#111827")
with col_top[1]:
    metric_card("Estado", status, subtitle="Suscripción", accent="#0D9488" if status == "ACTIVE" else "#B45309")
with col_top[2]:
    metric_card("Renovación", renewal, subtitle="Próximo ciclo", accent="#1E88E5")

# Acciones
st.subheader("Acciones rápidas")
portal = billing.get("manage_url")
col_action = st.columns(2)
with col_action[0]:
    if portal:
        st.link_button("Actualizar plan en Stripe", portal, type="primary")
    else:
        st.info("Portal no disponible. Asigna un cliente Stripe para habilitar el upgrade.")
with col_action[1]:
    st.markdown(pill("IA habilitada" if plan != "BASE" else "IA limitada en BASE", "info"), unsafe_allow_html=True)

# Detalle de consumo y límites
st.subheader("Límites del plan")
limits_features = limits.get("features") if isinstance(limits, dict) else {}
col_limits = st.columns(2)
with col_limits[0]:
    max_ia = limits.get("max_ia_cost", "—")
    max_sessions = limits.get("max_sessions", "—")
    st.markdown(f"- Límite IA mensual: **{max_ia} €**")
    st.markdown(f"- Sesiones mensuales: **{max_sessions}**")
with col_limits[1]:
    if isinstance(limits_features, dict):
        bullets = []
        if limits_features.get("ia_enabled") is not None:
            bullets.append(f"- IA: **{'incluida' if limits_features.get('ia_enabled') else 'no incluida'}**")
        if limits_features.get("billing_portal"):
            bullets.append("- Portal de facturación: **Sí**")
        if bullets:
            st.markdown("\n".join(bullets))
        else:
            st.info("Sin características declaradas.")
    else:
        st.info("Sin características declaradas.")
