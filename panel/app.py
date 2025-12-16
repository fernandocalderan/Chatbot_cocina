import streamlit as st

from auth import ensure_login
from utils import load_styles, render_quota_banner, render_quota_usage_bar, metric_card
from api_client import (
    get_quota_status,
    get_tenant_kpis,
    count_leads,
    count_appointments,
    get_ia_metrics,
    get_tenant_config,
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
try:
    st.switch_page("pages/00_Inicio.py")
except Exception:
    st.stop()

def hydrate_branding():
    if st.session_state.get("_branding_loaded"):
        return
    cfg = get_tenant_config() or {}
    st.session_state["tenant_name"] = cfg.get("name") or st.session_state.get("tenant_name", "Tu negocio")
    st.session_state["tenant_language"] = cfg.get("language") or st.session_state.get("tenant_language", "es")
    st.session_state["tenant_logo_url"] = cfg.get("logo_url") or st.session_state.get("tenant_logo_url")
    st.session_state["tenant_timezone"] = cfg.get("timezone") or st.session_state.get("tenant_timezone", "Europe/Madrid")
    st.session_state["tenant_currency"] = cfg.get("currency") or st.session_state.get("tenant_currency", "EUR")
    st.session_state["customer_code"] = st.session_state.get("customer_code") or cfg.get("customer_code")
    st.session_state["_branding_loaded"] = True

hydrate_branding()

tenant_name = st.session_state.get("tenant_name", "Tu negocio")
tenant_plan = str(st.session_state.get("tenant_plan", "BASE")).upper()
tenant_id = st.session_state.get("tenant_id")
tenant_logo = st.session_state.get("tenant_logo_url")
tenant_lang = st.session_state.get("tenant_language", "es").upper()
tenant_tz = st.session_state.get("tenant_timezone", "Europe/Madrid")
tenant_currency = st.session_state.get("tenant_currency", "EUR").upper()

# Encabezado branding
header_cols = st.columns([0.7, 0.3])
with header_cols[0]:
    st.title(f"{tenant_name}")
    st.caption("Estado del negocio, IA y métricas clave en un vistazo.")
    st.markdown(f"**Plan:** {tenant_plan} | **Idioma:** {tenant_lang} | **TZ:** {tenant_tz} | **Moneda:** {tenant_currency}")
with header_cols[1]:
    if tenant_logo:
        st.image(tenant_logo, width=140)
    else:
        st.markdown(
            """
            <div style="padding:10px;border:1px dashed #ccc;border-radius:8px;text-align:center;">
            Logo no configurado
            </div>
            """,
            unsafe_allow_html=True,
        )

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

# Tabs principales para mejor navegación
tab_overview, tab_branding = st.tabs(["📊 Resumen", "🎨 Branding & Accesos"])

with tab_overview:
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

    st.subheader("Cómo vamos")
    st.markdown(
        """
        - Revisa *Billing* para ajustar plan cuando estés en modo ahorro/bloqueo.
        - Usa *IA Usage* para detalles de coste y tokens.
        - Leads y Citas tienen filtros y detalle para seguimiento.
        """
    )

with tab_branding:
    st.subheader("Identidad del tenant")
    bc1, bc2 = st.columns([0.5, 0.5])
    with bc1:
        st.text_input("Nombre comercial", value=tenant_name, disabled=True)
        st.text_input("Idioma", value=tenant_lang, disabled=True)
        st.text_input("Timezone", value=tenant_tz, disabled=True)
        st.text_input("Moneda", value=tenant_currency, disabled=True)
    with bc2:
        st.text_input("Plan", value=tenant_plan, disabled=True)
        st.text_input("Tenant ID", value=tenant_id or "", disabled=True)
        st.text_input("Código comercial", value=st.session_state.get("customer_code", ""), disabled=True)
        if tenant_logo:
            st.image(tenant_logo, width=180)
    st.markdown("Para cambiar logo/branding, ve a la sección *Widget* o contacta soporte.")
    st.page_link("pages/07_Widget.py", label="Ir a configuración del Widget")
    st.page_link("pages/06_Billing.py", label="Ir a Billing")
