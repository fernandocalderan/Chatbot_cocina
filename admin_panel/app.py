import os
import streamlit as st
from pathlib import Path

from api_client import (
    admin_login,
    admin_overview,
    create_tenant,
    impersonate,
    issue_widget_token,
    list_tenants,
    toggle_maintenance,
    update_tenant,
)
from theme import FONT_FAMILY

st.set_page_config(page_title="Opunnence SuperAdmin", layout="wide")


def load_styles():
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        css = css_path.read_text()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_styles()

st.title("Opunnence — SuperAdmin")
st.caption("Control global de tenants, dominios y tokens del widget.")

admin_api_key = os.getenv("ADMIN_API_KEY")

with st.sidebar:
    if admin_api_key:
        st.success("Autenticado con ADMIN_API_KEY (bypass OIDC).")
        st.session_state["admin_token"] = None
        st.session_state["admin_api_key"] = admin_api_key
    else:
        st.subheader("Login OIDC SUPER_ADMIN")
        st.caption("Pega el ID token del IdP (OIDC) autorizado.")
        oidc_token = st.text_area("ID Token OIDC", height=150)
        if st.button("Iniciar sesión"):
            try:
                resp = admin_login(oidc_token)
                if resp and (resp.get("token") or resp.get("api_key")):
                    st.session_state["admin_token"] = resp.get("token")
                    st.session_state["admin_api_key"] = resp.get("api_key")
                    st.success(f"Autenticado: {resp.get('email') or 'api_key'}")
                else:
                    st.error("No se pudo iniciar sesión")
            except Exception as exc:
                st.error(f"Error: {exc}")

token = st.session_state.get("admin_token")
api_key = st.session_state.get("admin_api_key") or admin_api_key
if not token and not api_key:
    st.stop()

# Banner de impersonación (visible en todas las vistas)
impersonation_token = st.session_state.get("impersonation_token")
if impersonation_token:
    with st.container():
        st.markdown(
            """
            <div style="padding:12px;border:1px solid #f44336;background:#ffebee;border-radius:6px;margin-bottom:12px;">
            <strong>Modo impersonación activo:</strong> estás operando como TENANT. Sal del modo impersonación antes de realizar otras acciones.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Salir de impersonación"):
            st.session_state.pop("impersonation_token", None)
            st.experimental_rerun()

# Dashboard overview
ov = admin_overview(token) or {}
tenants = list_tenants(token) or []
saving = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "SAVING"]
locked = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "LOCKED"]

col_overview, col_errors = st.columns([2, 1])
with col_overview:
    st.subheader("Overview")
    st.metric("Tenants", ov.get("tenants", len(tenants)))
    st.metric("Leads", ov.get("leads", 0))
    st.metric("IA cost (mes)", f"{ov.get('ia_cost_month', 0):.2f} €")
with col_errors:
    st.subheader("Errores recientes")
    st.info("Integrar con logs externos (CloudWatch/Loki).")

col_kpi = st.columns(4)
col_kpi[0].metric("Tenants activos", len(tenants))
col_kpi[1].metric("En SAVING", len(saving))
col_kpi[2].metric("En LOCKED", len(locked))
col_kpi[3].metric("Coste IA global", f"{ov.get('ia_cost_month', 0):.2f} €")

st.subheader("Tenants en riesgo")
risk = saving + locked
if risk:
    for t in risk:
        st.markdown(f"- **{t.get('name')}** — {t.get('usage_mode')} — plan {t.get('plan')} — IA uso {t.get('usage_monthly', 0)} / {t.get('usage_limit_monthly') or 'N/D'}")
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

st.divider()
st.subheader("Tenants")
for t in tenants:
    with st.expander(f"{t.get('name')} — {t.get('plan')} — {t.get('id')}"):
        cols = st.columns(3)
        new_plan = cols[0].selectbox("Plan", ["BASE", "PRO", "ELITE"], index=["BASE", "PRO", "ELITE"].index(t.get("plan", "BASE")))
        new_limit = cols[1].number_input("Límite IA €", value=float(t.get("ia_monthly_limit_eur", 0)), min_value=0.0, step=5.0)
        maint = cols[2].checkbox("Mantenimiento", value=bool(t.get("maintenance")))
        origins = st.text_area("Allowed origins (coma)", value=",".join(t.get("allowed_origins") or []))
        use_ia = st.checkbox("IA habilitada", value=bool(t.get("ia_enabled", True)))
        if st.button("Guardar", key=f"save-{t['id']}"):
            payload = {
                "plan": new_plan,
                "ia_monthly_limit_eur": new_limit,
                "allowed_origins": [o.strip() for o in origins.split(",") if o.strip()],
                "maintenance": maint,
                "ia_enabled": use_ia,
                "use_ia": use_ia,
            }
            res = update_tenant(token, t["id"], payload)
            st.success(f"Actualizado: {res}")
        if st.button("ON/OFF mantenimiento", key=f"maint-{t['id']}"):
            res = toggle_maintenance(token, t["id"], not maint)
            st.success(res)
        st.markdown("### Token del widget")
        col_t1, col_t2 = st.columns(2)
        allowed_origin = col_t1.text_input("Dominio", value=(t.get("allowed_origins") or [""])[0] if t.get("allowed_origins") else "")
        ttl = col_t2.slider("TTL minutos", 15, 60, 30)
        if st.button("Generar token", key=f"token-{t['id']}"):
            res = issue_widget_token(token, t["id"], allowed_origin, ttl_minutes=ttl)
            if "token" in res:
                st.code(res["token"], language="text")
            else:
                st.error(res)
        if st.button("Impersonar", key=f"imp-{t['id']}"):
            res = impersonate(token, t["id"])
            if "token" in res:
                st.session_state["impersonation_token"] = res["token"]
                st.code(res["token"], language="text")
                st.info("Impersonación almacenada en sesión local. Úsalo en el panel de tenant o sal para limpiar.")
            else:
                st.error(res)

st.divider()
st.subheader("Crear tenant")
with st.form("create-tenant-form"):
    name = st.text_input("Nombre")
    contact = st.text_input("Email contacto")
    plan = st.selectbox("Plan", ["BASE", "PRO", "ELITE"])
    origins_new = st.text_input("Allowed origins (coma)")
    limit = st.number_input("Límite IA €", min_value=0.0, step=5.0, value=0.0)
    maint_new = st.checkbox("Mantenimiento inicial", value=False)
    use_ia_new = st.checkbox("IA habilitada", value=True)
    submitted = st.form_submit_button("Crear")
    if submitted:
        payload = {
            "name": name,
            "contact_email": contact or None,
            "plan": plan,
            "ia_monthly_limit_eur": limit,
            "allowed_origins": [o.strip() for o in origins_new.split(",") if o.strip()],
            "maintenance": maint_new,
            "use_ia": use_ia_new,
            "ia_enabled": use_ia_new,
        }
        res = create_tenant(token, payload)
        if res and "id" in res:
            st.success(f"Tenant creado: {res['id']}")
        else:
            st.error(res)
