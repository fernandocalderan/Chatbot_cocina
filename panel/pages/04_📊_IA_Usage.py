import math
import streamlit as st
import pandas as pd

from api_client import api_get, get_quota_status
from auth import ensure_login
from nav import render_sidebar, legacy_redirect_with_tab, nav_v2_enabled
from utils import load_styles, render_quota_banner, render_quota_usage_bar, metric_card, empty_state

st.set_page_config(
    page_title="Consumo de IA",
    page_icon="🤖",
    layout="wide",
)

load_styles()
ensure_login()
if nav_v2_enabled():
    legacy_redirect_with_tab("/IA_Usage", "pages/automatizacion.py", "nivel")
    st.stop()
render_sidebar()

st.title("📊 Consumo de IA")
st.caption("Coste, tokens y estado de cuota para el tenant activo.")
st.info("Resumen simplificado: Automatización → Nivel de automatización.")
if st.button("Abrir Automatización", use_container_width=True):
    st.switch_page("pages/automatizacion.py")

# --- Validación de sesión/rol ---
role = st.session_state.get("role")
if role not in {"SUPER_ADMIN", "ADMIN"}:
    empty_state("Acceso restringido", "Solo admin puede ver esta vista técnica. El asistente sigue activo.", icon="🔒")
    st.stop()

token = st.session_state.get("token") or st.session_state.get("access_token")
tenant_id = st.session_state.get("tenant_id")
if not tenant_id:
    st.warning("Selecciona un tenant en la barra lateral para ver sus métricas IA.")
    st.stop()
if not token:
    st.error("Sesión no encontrada. Vuelve a iniciar sesión.")
    st.stop()

# --- Fetch datos ---
with st.spinner("Consultando métricas IA..."):
    res = api_get(f"/metrics/ia/tenant/{tenant_id}")
    quota = get_quota_status()

if not res or not isinstance(res, dict):
    st.error("No se pudieron obtener métricas IA desde la API.")
    st.stop()

monthly = res.get("monthly", {}) or {}
latest = res.get("latest", []) or []
qs = quota.get("quota_status") if isinstance(quota, dict) else None
needs = bool(qs.get("needs_upgrade_notice")) if isinstance(qs, dict) else False
render_quota_banner(qs, needs_upgrade=needs, upgrade_url=res.get("manage_url"))
render_quota_usage_bar(qs, label="Consumo IA mensual")

# --- Resumen ---
total_cost = float(monthly.get("total_cost_eur", 0.0) or 0.0)
tokens_in = int(monthly.get("tokens_in", 0) or 0)
tokens_out = int(monthly.get("tokens_out", 0) or 0)
PLAN_LIMITS_EUR = {"BASE": 10.0, "PRO": 25.0, "ELITE": 100.0}
plan = str(st.session_state.get("tenant_plan", "BASE")).upper()
limit_eur = PLAN_LIMITS_EUR.get(plan, PLAN_LIMITS_EUR["BASE"])
percentage = min((total_cost / limit_eur) * 100.0, 100.0) if limit_eur else 0.0

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Coste mensual", f"{total_cost:.2f} €", subtitle="IA usage", accent="#1E88E5")
with col2:
    metric_card("Tokens IN", f"{tokens_in:,}", subtitle="Mes en curso", accent="#0D9488")
with col3:
    metric_card("Tokens OUT", f"{tokens_out:,}", subtitle="Mes en curso", accent="#0D9488")
with col4:
    metric_card("Uso del límite", f"{percentage:.0f} %", subtitle=f"Plan {plan}", accent="#B45309" if percentage >= 80 else "#1E88E5")

st.subheader("Consumo respecto al límite mensual")
st.progress(percentage / 100.0 if limit_eur else 0.0)

# ===========================
# Serie temporal de consumo IA
# ===========================
st.subheader("Evolución temporal del consumo IA")

if latest:
    df_ts = pd.DataFrame(latest)
    if "date" in df_ts.columns:
        df_ts["date"] = pd.to_datetime(df_ts["date"]).dt.date

    group_cols = ["date"]
    agg_map = {
        "cost_eur": "sum",
        "tokens_in": "sum",
        "tokens_out": "sum",
    }
    agg_map = {k: v for k, v in agg_map.items() if k in df_ts.columns}

    if agg_map:
        daily = (
            df_ts.groupby(group_cols)
            .agg(agg_map)
            .reset_index()
            .sort_values("date")
        )
        daily.set_index("date", inplace=True)

        col_left, col_right = st.columns(2)
        if "cost_eur" in daily.columns:
            col_left.markdown("**Coste diario (€)**")
            col_left.line_chart(daily[["cost_eur"]])

        token_cols = [c for c in ["tokens_in", "tokens_out"] if c in daily.columns]
        if token_cols:
            col_right.markdown("**Tokens diarios (IN / OUT)**")
            col_right.line_chart(daily[token_cols])
    else:
        st.info("No hay datos suficientes para construir la serie temporal de consumo.")
else:
    st.info("No se encontraron registros para generar series temporales.")

# --- Tabla de registros ---
st.subheader("Registros detallados")
if latest:
    df = pd.DataFrame(latest)
    for col in ("date", "created_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    st.dataframe(df, use_container_width=True, height=420)
else:
    st.info("No se encontraron registros de uso IA para este tenant.")
