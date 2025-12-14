import streamlit as st

from auth import ensure_login
from utils import load_styles, render_quota_banner, render_quota_usage_bar, metric_card, pill
from api_client import (
    get_quota_status,
    get_tenant_kpis,
    count_leads,
    count_appointments,
    get_ia_metrics,
)

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
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

# Datos con tolerancia a errores de API
quota_raw = get_quota_status() or {}
quota_status = quota_raw.get("quota_status") if isinstance(quota_raw, dict) else {}
if not isinstance(quota_status, dict):
    quota_status = {}

kpis_raw = get_tenant_kpis() or {}
kpi_data = kpis_raw.get("kpis") if isinstance(kpis_raw, dict) and isinstance(kpis_raw.get("kpis"), dict) else {}

ia_metrics = get_ia_metrics(tenant_id) if tenant_id else {}
monthly = ia_metrics.get("monthly") if isinstance(ia_metrics, dict) and isinstance(ia_metrics.get("monthly"), dict) else {}

spent = float((monthly.get("total_cost_eur") if isinstance(monthly, dict) else 0.0) or 0.0)
limit = float(
    (quota_status.get("limit_eur") if isinstance(quota_status, dict) else 0.0)
    or (kpi_data.get("ai_limit_eur") if isinstance(kpi_data, dict) else 0.0)
    or 0.0
)
usage_pct = min((spent / limit) * 100.0, 100.0) if limit else 0.0

def _safe_count(fn, **kwargs) -> int:
    try:
        value = fn(**kwargs)
        return int(value or 0)
    except Exception:
        return 0

leads_total = _safe_count(count_leads)
appointments_confirmed = _safe_count(count_appointments, status="confirmed")

api_status_codes = []
for payload in (quota_raw, kpis_raw, ia_metrics):
    if isinstance(payload, dict) and "status_code" in payload:
        api_status_codes.append(payload.get("status_code"))
if any(code in (401, 403) for code in api_status_codes):
    st.info("No se pudieron cargar algunos datos (código 401/403). Mostramos valores por defecto.")

# Hero
st.title(tenant_name)
hero_cols = st.columns(3)
with hero_cols[0]:
    st.markdown(pill(f"Plan {tenant_plan}", tone="info"), unsafe_allow_html=True)
with hero_cols[1]:
    status_mode = "ACTIVE"
    if isinstance(quota_status, dict):
        status_mode = str(quota_status.get("mode") or quota_status.get("quota_status") or "ACTIVE")
    status_mode_upper = status_mode.upper()
    tone = "success" if status_mode_upper == "ACTIVE" else ("warning" if status_mode_upper == "SAVING" else "error")
    st.markdown(pill(f"Estado IA: {status_mode_upper}", tone=tone), unsafe_allow_html=True)
with hero_cols[2]:
    st.write("")
    st.write("")
    if st.button("Gestionar plan y consumo"):
        try:
            st.switch_page("pages/06_Billing.py")
        except Exception:
            pass

render_quota_banner(quota_status, needs_upgrade=bool((quota_status or {}).get("needs_upgrade_notice")))
render_quota_usage_bar(quota_status, label="Consumo IA mensual")

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Leads del mes", f"{leads_total}", subtitle="este mes")
with col2:
    metric_card("Citas confirmadas", f"{appointments_confirmed}", subtitle="este mes", accent="#0D9488")
with col3:
    metric_card("Coste IA (mes)", f"{spent:.2f} €", subtitle="uso actual", accent="#1E88E5")
with col4:
    metric_card("% uso límite IA", f"{usage_pct:.0f} %", subtitle="respecto a tu plan", accent="#B45309" if usage_pct >= 80 else "#1E88E5")

# Consumo IA barra
st.subheader("Consumo de IA")
st.markdown(f"**{spent:.2f} € / {limit if limit else '—'} €**")
st.progress(usage_pct / 100.0 if limit else 0.0)

st.caption("Consulta más detalle y gestiona el plan en la sección Billing.")
