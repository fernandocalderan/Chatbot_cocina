import math
import streamlit as st
import pandas as pd

from api_client import api_get

st.set_page_config(
    page_title="Consumo de IA",
    page_icon="🤖",
    layout="wide",
)

st.title("📊 Consumo de IA por Tenant")
st.caption(
    "Monitoriza el coste mensual de IA, tokens consumidos y registros recientes por tenant."
)

# --- Validación de sesión/rol ---
role = st.session_state.get("role")
if role not in {"SUPER_ADMIN", "ADMIN"}:
    st.error("Acceso restringido: solo super-admin/admin puede ver esta página.")
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

if not res or not isinstance(res, dict):
    st.error("No se pudieron obtener métricas IA desde la API.")
    st.stop()

monthly = res.get("monthly", {}) or {}
latest = res.get("latest", []) or []

# --- Resumen ---
st.subheader("Resumen mensual")
total_cost = float(monthly.get("total_cost_eur", 0.0) or 0.0)
tokens_in = int(monthly.get("tokens_in", 0) or 0)
tokens_out = int(monthly.get("tokens_out", 0) or 0)

PLAN_LIMITS_EUR = {"BASE": 10.0, "PRO": 25.0, "ELITE": 100.0}
plan = str(st.session_state.get("tenant_plan", "BASE")).upper()
limit_eur = PLAN_LIMITS_EUR.get(plan, PLAN_LIMITS_EUR["BASE"])
percentage = min((total_cost / limit_eur) * 100.0, 100.0) if limit_eur else 0.0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💶 Coste mensual (€)", f"{total_cost:.4f} €")
col2.metric("🔢 Tokens IN", f"{tokens_in:,}")
col3.metric("🔢 Tokens OUT", f"{tokens_out:,}")
col4.metric("📈 Uso del límite (%)", f"{percentage:.2f} %")

st.subheader("Consumo respecto al límite mensual")
st.progress(percentage / 100.0 if limit_eur else 0.0)

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
