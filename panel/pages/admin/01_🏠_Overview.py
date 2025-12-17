import datetime
import streamlit as st

from api_client import admin_login, admin_overview, list_tenants
from utils import load_styles, metric_card, pill

st.set_page_config(page_title="Platform Overview", page_icon="🏠", layout="wide")
load_styles()

# Auth: solo SUPER_ADMIN (usa admin_token/api_key en session_state)
admin_token = st.session_state.get("admin_token")
admin_api_key = st.session_state.get("admin_api_key") or st.session_state.get("ADMIN_API_KEY") or None
if not admin_token and not admin_api_key:
    st.error("Acceso restringido. Inicia sesión como SUPER_ADMIN desde admin_panel.")
    st.stop()

st.title("Platform Overview")
st.caption(f"Estado global — {datetime.date.today().isoformat()}")

# Fetch data
overview = admin_overview(admin_token) or {}
tenants = list_tenants(admin_token) or []
saving = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "SAVING"]
locked = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "LOCKED"]

# KPIs
col_kpi = st.columns(4)
col_kpi[0].metric("Tenants activos", overview.get("tenants", len(tenants)))
col_kpi[1].metric("IA cost (mes)", f"{overview.get('ia_cost_month', 0):.2f} €")
col_kpi[2].metric("En SAVING", len(saving))
col_kpi[3].metric("En LOCKED", len(locked))

# Banner si hay LOCKED
if locked:
    st.warning(f"{len(locked)} tenants en LOCKED. Priorizar contacto/upgrade.")

# Gráfico top 10 coste IA
st.subheader("Top 10 tenants por coste IA (mes)")
ordered = sorted(tenants, key=lambda x: float(x.get("usage_monthly") or 0), reverse=True)[:10]
names = [t.get("name") for t in ordered]
costs = [float(t.get("usage_monthly") or 0) for t in ordered]
if costs and any(costs):
    st.bar_chart({"Tenant": names, "IA Cost": costs}, x="Tenant", y="IA Cost")
else:
    st.info("Sin consumo IA registrado todavía.")

# Tenants en riesgo
st.subheader("Tenants en riesgo (SAVING / LOCKED)")
risk = sorted(saving + locked, key=lambda t: 0 if str(t.get("usage_mode") or "").upper() == "LOCKED" else 1)
if not risk:
    st.info("Sin tenants en riesgo ahora mismo.")
else:
    for t in risk:
        quota = str(t.get("usage_mode") or "").upper()
        tone = "error" if quota == "LOCKED" else "warning"
        limit = t.get("usage_limit_monthly") or 0
        spent = float(t.get("usage_monthly") or 0)
        pct = min((spent / limit) * 100.0, 100.0) if limit else 0.0
        plan = t.get("plan") or "N/D"
        st.markdown(
            f"""
            <div style="border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;margin-bottom:8px;background:#fff;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <div style="font-weight:700;font-size:16px;">{t.get('name')}</div>
                  <div style="color:#6B7280;font-size:13px;">Plan {plan}</div>
	                  <div style="margin-top:4px;">{pill(f"Quota {quota}", tone=tone)} {pill(f"Uso {pct:.0f}%", tone='warning' if pct>=80 else 'info')}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-weight:700;font-size:16px;">{spent:.2f} €</div>
                  <div style="color:#6B7280;font-size:12px;">consumo IA mes</div>
                  <a href="#" style="font-size:12px;color:#1E88E5;text-decoration:none;font-weight:600;" onclick="window.location.href='#'">Ver tenant</a>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
