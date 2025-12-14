import streamlit as st

from auth import ensure_login
from utils import load_styles, render_quota_banner, render_quota_usage_bar, metric_card
from api_client import (
    get_quota_status,
    get_tenant_kpis,
    count_leads,
    count_appointments,
    get_ia_metrics,
)

st.set_page_config(page_title="Panel Operativo", layout="wide")
load_styles()

# Redirige al login si no hay token
if "token" not in st.session_state:
    try:
        st.switch_page("pages/auth.py")
    except Exception:
        st.stop()
ensure_login()

tenant_name = st.session_state.get("tenant_name", "Tu negocio")
tenant_plan = str(st.session_state.get("tenant_plan", "BASE")).upper()
tenant_id = st.session_state.get("tenant_id")

st.title(f"{tenant_name}")
st.caption("Estado del negocio, IA y métricas clave en un vistazo.")

# Datos
quota = get_quota_status() or {}
quota_status = quota.get("quota_status") if isinstance(quota, dict) else None
kpis = get_tenant_kpis() or {}
kpi_data = kpis.get("kpis") if isinstance(kpis, dict) else {}
ia_metrics = get_ia_metrics(tenant_id) if tenant_id else {}

leads_total = count_leads()
appointments_confirmed = count_appointments(status="confirmed")
ia_cost = float((ia_metrics.get("monthly") or {}).get("total_cost_eur", 0.0) or 0.0)
ia_limit = float((quota_status or {}).get("limit_eur") or kpi_data.get("ai_limit_eur") or 0.0)
usage_pct = 0.0
if ia_limit:
    usage_pct = min((ia_cost / ia_limit) * 100.0, 100.0)

# Hero / banners
render_quota_banner(quota_status, needs_upgrade=bool((quota_status or {}).get("needs_upgrade_notice")))
render_quota_usage_bar(quota_status, label="Consumo IA mensual")

# Metric cards
cols = st.columns(4)
with cols[0]:
    metric_card("Leads (mes)", f"{leads_total}", subtitle="Capturados")
with cols[1]:
    metric_card("Citas confirmadas", f"{appointments_confirmed}", subtitle="Agenda", accent="#0D9488")
with cols[2]:
    metric_card("Coste IA (mes)", f"{ia_cost:.2f} €", subtitle=f"Plan {tenant_plan}", accent="#1E88E5")
with cols[3]:
    metric_card("% uso límite IA", f"{usage_pct:.0f} %", subtitle="Consumo", accent="#B45309" if usage_pct >= 80 else "#1E88E5")

# Bloques secundarios
st.subheader("Cómo vamos")
st.markdown(
    """
    - Revisa *Billing* para ajustar plan cuando estés en modo ahorro/bloqueo.
    - Usa *IA Usage* para detalles de coste y tokens.
    - Leads y Citas tienen filtros y detalle para seguimiento.
    """
)
