import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import admin_alerts, admin_health, admin_overview, admin_recent_errors, list_tenants
from admin_panel.ui import init_page, metric_card, pill, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="SuperAdmin — Overview", icon="📊")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")


st.title("Overview")
st.caption("Salud del sistema, alertas y KPIs principales.")

with st.spinner("Cargando overview…"):
    ov = admin_overview(ctx.token, api_key=ctx.api_key) or {}
    _show_api_error(ov, "No se pudo cargar el overview")

    tenants_payload = list_tenants(ctx.token, api_key=ctx.api_key)
    tenants = tenants_payload if isinstance(tenants_payload, list) else []
    _show_api_error(tenants_payload, "No se pudo cargar el listado de tenants")

saving = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "SAVING"]
locked = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "LOCKED"]

col_overview, col_errors = st.columns([2, 1])
with col_overview:
    st.subheader("KPIs")
    k1, k2, k3 = st.columns(3)
    with k1:
        metric_card("Tenants", f"{ov.get('tenants', len(tenants))}")
    with k2:
        metric_card("Leads", f"{ov.get('leads', 0)}", accent="#0D9488")
    with k3:
        metric_card("IA cost (mes)", f"{ov.get('ia_cost_month', 0):.2f} €", accent="#1E88E5")
with col_errors:
    st.subheader("Errores recientes")
    err_payload = admin_recent_errors(ctx.token, api_key=ctx.api_key) or {}
    _show_api_error(err_payload, "No se pudieron cargar errores recientes")
    errs = err_payload.get("items") or []
    if errs:
        for err in errs[:5]:
            st.markdown(f"- {err.get('timestamp', '')} — {err.get('level', '')}: {err.get('message')}")
        if len(errs) > 5:
            st.caption(f"... y {len(errs)-5} más")
    else:
        st.info("Sin errores recientes")

health = admin_health(ctx.token, api_key=ctx.api_key) or {}
_show_api_error(health, "No se pudo cargar el estado de health")
st.subheader("Health")
col_h1, col_h2, col_h3, col_h4 = st.columns(4)

def _tone(v: str | None) -> str:
    if not v:
        return "info"
    vv = str(v).upper()
    if vv in {"UP", "OK"}:
        return "success"
    return "warning"

with col_h1:
    st.markdown(f"API: {pill(str(health.get('api', 'N/A')), _tone(health.get('api')))}", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"DB: {pill(str(health.get('db', 'N/A')), _tone(health.get('db')))}", unsafe_allow_html=True)
with col_h3:
    st.markdown(f"Redis: {pill(str(health.get('redis', 'N/A')), _tone(health.get('redis')))}", unsafe_allow_html=True)
with col_h4:
    st.markdown(
        f"IA: {pill(str(health.get('ia_provider', 'N/A')), _tone(health.get('ia_provider')))}",
        unsafe_allow_html=True,
    )
if st.button("Refrescar health"):
    st.rerun()

with st.container():
    st.subheader("Alertas activas")
    alert_payload = admin_alerts(ctx.token, api_key=ctx.api_key) or {}
    _show_api_error(alert_payload, "No se pudieron cargar alertas")
    alerts = alert_payload.get("items") or []
    if not alerts:
        st.info("Sin alertas")
    else:
        for a in alerts:
            sev = a.get("severity", "info")
            icon = "🟢"
            if sev == "warning":
                icon = "🟠"
            elif sev == "critical":
                icon = "🔴"
            st.markdown(f"- {icon} {a.get('tenant')}: {a.get('message')}")

col_kpi = st.columns(4)
col_kpi[0].metric("Tenants activos", len(tenants))
col_kpi[1].metric("En SAVING", len(saving))
col_kpi[2].metric("En LOCKED", len(locked))
col_kpi[3].metric("Coste IA global", f"{ov.get('ia_cost_month', 0):.2f} €")

st.subheader("Tenants en riesgo")
risk = saving + locked
if risk:
    for t in risk:
        st.markdown(
            f"- **{t.get('name')}** — {t.get('usage_mode')} — plan {t.get('plan')} — IA uso {t.get('usage_monthly', 0)} / {t.get('usage_limit_monthly') or 'N/D'}"
        )
else:
    st.info("Sin tenants en riesgo ahora mismo.")

if tenants:
    st.subheader("Top 10 coste IA")
    ordered = sorted(tenants, key=lambda x: float(x.get("usage_monthly") or 0), reverse=True)[:10]
    names = [t.get("name") for t in ordered]
    costs = [float(t.get("usage_monthly") or 0) for t in ordered]
    if costs and any(costs):
        chart_data = {"Tenant": names, "IA Cost": costs}
        st.bar_chart(chart_data, x="Tenant", y="IA Cost")
    else:
        st.info("Aún no hay consumo IA registrado.")
