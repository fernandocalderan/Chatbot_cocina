import streamlit as st

from auth import ensure_login
from utils import load_styles, metric_card
from api_client import (
    count_leads,
    count_appointments,
    get_ia_metrics,
    get_quota_status,
    get_tenant_kpis,
)

st.set_page_config(page_title="Inicio", page_icon="🏠", layout="wide")
load_styles()
ensure_login()

tenant_name = st.session_state.get("tenant_name", "Tu negocio")
tenant_plan = str(st.session_state.get("tenant_plan", "BASE")).upper()
tenant_id = st.session_state.get("tenant_id")

# Datos principales tolerantes a fallo
quota = get_quota_status() or {}
quota_status = quota.get("quota_status") if isinstance(quota, dict) else {}
if not isinstance(quota_status, dict):
    quota_status = {}
kpis = get_tenant_kpis() or {}
kpi_data = kpis.get("kpis") if isinstance(kpis, dict) and isinstance(kpis.get("kpis"), dict) else {}
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
leads_new = _safe_count(count_leads, status="new")
appointments_today = _safe_count(count_appointments, status="today")

st.title("Inicio")
st.caption("Qué hacer hoy y cómo va tu negocio.")

# Acción inmediata
st.subheader("Acción inmediata")
action_cols = st.columns(3)
with action_cols[0]:
    if st.button(f"Leads nuevos sin contactar: {leads_new}", use_container_width=True):
        try:
            st.switch_page("pages/02_Oportunidades.py")
        except Exception:
            pass
with action_cols[1]:
    if st.button(f"Citas para hoy: {appointments_today}", use_container_width=True):
        try:
            st.switch_page("pages/03_Agenda.py")
        except Exception:
            pass
with action_cols[2]:
    # Prioritarios = heurística: leads confirmados/próximos
    if st.button("Oportunidades prioritarias: Revisar ahora", use_container_width=True):
        try:
            st.switch_page("pages/02_Oportunidades.py")
        except Exception:
            pass

# Resumen de rendimiento
st.subheader("Resumen de rendimiento")
cols = st.columns(3)
with cols[0]:
    metric_card("Leads este mes", f"{leads_total}", subtitle="")
with cols[1]:
    metric_card("Citas confirmadas", f"{appointments_confirmed}", subtitle="este mes", accent="#0D9488")
with cols[2]:
    ratio = 0
    try:
        ratio = (appointments_confirmed / leads_total * 100) if leads_total else 0
    except Exception:
        ratio = 0
    metric_card("Ratio Lead → Cita", f"{ratio:.0f} %", subtitle="", accent="#1E88E5")

# El asistente trabaja por ti
st.subheader("El asistente trabaja por ti")
convos = int((monthly.get("total_interactions") if isinstance(monthly, dict) else 0) or 0)
autogen = int((monthly.get("leads_generated") if isinstance(monthly, dict) else 0) or 0)
st.markdown(
    f"""
    - El asistente ha atendido **{convos}** conversaciones esta semana.
    - Ha generado **{autogen}** oportunidades automáticamente.
    """
)

# Mensaje de error amable
api_status_codes = []
for payload in (quota, kpis, ia_metrics):
    if isinstance(payload, dict) and "status_code" in payload:
        api_status_codes.append(payload.get("status_code"))
if any(code in (500, 502, 503, 504) for code in api_status_codes):
    st.info("Estamos teniendo un problema temporal al cargar algunos datos. El asistente sigue funcionando.")
