import os
import streamlit as st
from pathlib import Path

from api_client import (
    admin_login,
    admin_overview,
    create_tenant,
    get_vertical,
    impersonate,
    issue_widget_token,
    admin_health,
    admin_recent_errors,
    admin_alerts,
    exclude_tenant,
    issue_magic_link,
    list_tenants,
    list_verticals,
    revoke_widget_tokens,
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

vertical_payload = list_verticals(token) or {}
vertical_items_raw = vertical_payload.get("items") or []
vertical_items = [v for v in vertical_items_raw if isinstance(v, dict) and v.get("key")]
vertical_items = sorted(
    vertical_items,
    key=lambda v: str(v.get("label") or v.get("key") or "").lower(),
)
vertical_keys = [v.get("key") for v in vertical_items if v.get("key")]
vertical_labels = {v.get("key"): v.get("label") for v in vertical_items if v.get("key")}
vertical_by_key = {v.get("key"): v for v in vertical_items if v.get("key")}

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

tabs = st.tabs(["📊 Overview", "🏢 Tenants", "🧩 Verticals", "➕ Crear tenant"])

with tabs[0]:
    ov = admin_overview(token) or {}
    tenants = list_tenants(token) or []
    saving = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "SAVING"]
    locked = [t for t in tenants if str(t.get("usage_mode") or "").upper() == "LOCKED"]

    col_overview, col_errors = st.columns([2, 1])
    with col_overview:
        st.subheader("KPIs")
        st.metric("Tenants", ov.get("tenants", len(tenants)))
        st.metric("Leads", ov.get("leads", 0))
        st.metric("IA cost (mes)", f"{ov.get('ia_cost_month', 0):.2f} €")
    with col_errors:
        st.subheader("Errores recientes")
        err_payload = admin_recent_errors(token) or {}
        errs = err_payload.get("items") or []
        if errs:
            for err in errs[:5]:
                st.markdown(f"- {err.get('timestamp', '')} — {err.get('level', '')}: {err.get('message')}")
            if len(errs) > 5:
                st.caption(f"... y {len(errs)-5} más")
        else:
            st.info("Sin errores recientes")

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    health = admin_health(token) or {}
    status_badge = lambda v: ("🟢" if v in ("UP", "OK") else "🟠") if v else "⚪"
    col_h1.metric("API", f"{status_badge(health.get('api'))} {health.get('api', 'N/A')}")
    col_h2.metric("DB", f"{status_badge(health.get('db'))} {health.get('db', 'N/A')}")
    col_h3.metric("Redis", f"{status_badge(health.get('redis'))} {health.get('redis', 'N/A')}")
    col_h4.metric("IA", f"{status_badge(health.get('ia_provider'))} {health.get('ia_provider', 'N/A')}")
    if st.button("Refrescar health"):
        st.rerun()

    alerts_box = st.container()
    with alerts_box:
        st.subheader("Alertas activas")
        alert_payload = admin_alerts(token) or {}
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

with tabs[1]:
    search_text = st.text_input(
        "Buscar tenant (email, nombre o código)",
        value="",
        placeholder="Ej: demo@kitchens.com | Demo Kitchens | OPN-000123",
    )
    tenants = list_tenants(token, search_text.strip() or None) or []
    st.caption(f"Resultados: {len(tenants)}")

    for t in tenants:
        code = t.get("customer_code") or "N/D"
        with st.expander(f"{t.get('name')} — {t.get('plan')} — {code} — {t.get('id')}"):
            st.text_input("Código comercial", value=code, disabled=True, key=f"code-{t['id']}")
            if vertical_keys:
                current_vertical = t.get("vertical_key") or vertical_keys[0]
                st.text_input(
                    "Vertical actual",
                    value=vertical_labels.get(current_vertical, current_vertical),
                    disabled=True,
                    key=f"vertical-label-{t['id']}",
                )

            st.markdown("**Plan y Billing**")
            cols = st.columns(3)
            new_plan = cols[0].selectbox(
                "Plan",
                ["BASE", "PRO", "ELITE"],
                index=["BASE", "PRO", "ELITE"].index(t.get("plan", "BASE")),
                key=f"plan-{t['id']}",
            )
            new_limit = cols[1].number_input(
                "Límite IA €",
                value=float(t.get("ia_monthly_limit_eur", 0)),
                min_value=0.0,
                step=5.0,
                key=f"limit-{t['id']}",
            )
            maint = cols[2].checkbox("Mantenimiento", value=bool(t.get("maintenance")), key=f"maint-check-{t['id']}")
            billing_status = st.selectbox(
                "Billing status",
                ["ACTIVE", "PAST_DUE", "CANCELED", "INCOMPLETE"],
                index=["ACTIVE", "PAST_DUE", "CANCELED", "INCOMPLETE"].index(str(t.get("billing_status") or "ACTIVE")),
                key=f"billing-{t['id']}",
            )
            origins = st.text_area("Allowed origins (coma)", value=",".join(t.get("allowed_origins") or []), key=f"origins-{t['id']}")
            use_ia = st.checkbox("IA habilitada", value=bool(t.get("ia_enabled", True)), key=f"use-ia-{t['id']}")
            new_vertical = None
            force_vertical = False
            if vertical_keys:
                new_vertical = st.selectbox(
                    "Cambiar vertical",
                    vertical_keys,
                    index=vertical_keys.index(current_vertical) if current_vertical in vertical_keys else 0,
                    format_func=lambda v: vertical_labels.get(v, v),
                    key=f"vertical-{t['id']}",
                )
                force_vertical = st.checkbox("Forzar cambio de vertical", value=False, key=f"force-vertical-{t['id']}")

            if st.button("Guardar", key=f"save-{t['id']}"):
                payload = {
                    "plan": new_plan,
                    "ia_monthly_limit_eur": new_limit,
                    "allowed_origins": [o.strip() for o in origins.split(",") if o.strip()],
                    "maintenance": maint,
                    "ia_enabled": use_ia,
                    "use_ia": use_ia,
                    "billing_status": billing_status,
                }
                if new_vertical and new_vertical != current_vertical:
                    payload["vertical_key"] = new_vertical
                    payload["force_vertical"] = force_vertical
                res = update_tenant(token, t["id"], payload)
                st.success(f"Actualizado: {res}")
            if st.button("ON/OFF mantenimiento", key=f"maint-{t['id']}"):
                res = toggle_maintenance(token, t["id"], not maint)
                st.success(res)

            st.markdown("**Accesos y Widget**")
            col_t1, col_t2 = st.columns(2)
            allowed_origin = col_t1.text_input(
                "Dominio",
                value=(t.get("allowed_origins") or [""])[0] if t.get("allowed_origins") else "",
                key=f"allowed-origin-{t['id']}",
            )
            ttl = col_t2.slider("TTL minutos", 15, 60, 30, key=f"ttl-{t['id']}")
            if st.button("Generar token widget", key=f"token-{t['id']}"):
                res = issue_widget_token(token, t["id"], allowed_origin, ttl_minutes=ttl)
                if "token" in res:
                    st.code(res["token"], language="text")
                else:
                    st.error(res)
            st.caption(f"Última revocación: {t.get('widget_tokens_revoked_before') or 'n/d'}")
            with st.expander("Revocar todos los tokens del widget", expanded=False):
                confirm_text = st.text_input("Escribe REVOCAR para confirmar", key=f"revoke-confirm-{t['id']}")
                if st.button("Revocar tokens", key=f"revoke-{t['id']}"):
                    if confirm_text.strip().upper() != "REVOCAR":
                        st.warning("Escribe REVOCAR para continuar.")
                    else:
                        res = revoke_widget_tokens(token, t["id"])
                        if "revoked_before" in res:
                            st.success(f"Revocados. Nueva marca: {res['revoked_before']}")
                        else:
                            st.error(res)
            with st.expander("Magic link (acceso tenant)", expanded=False):
                ml_email = st.text_input("Email destino", value=t.get("contact_email") or "", key=f"ml-email-{t['id']}")
                if st.button("Generar magic link", key=f"ml-btn-{t['id']}"):
                    res = issue_magic_link(token, t["id"], ml_email.strip() or None)
                    if res.get("token"):
                        st.code(res["token"], language="text")
                        st.success(f"Enlace enviado/emitido para {res.get('email')}")
                    else:
                        st.error(res)

            st.markdown("**Estado y seguridad**")
            with st.expander("Excluir tenant", expanded=False):
                excl_reason = st.text_input("Motivo (opcional)", key=f"exclude-reason-{t['id']}")
                excl_confirm = st.text_input("Escribe EXCLUIR para confirmar", key=f"exclude-confirm-{t['id']}")
                if st.button("Excluir tenant", key=f"exclude-{t['id']}"):
                    if excl_confirm.strip().upper() != "EXCLUIR":
                        st.warning("Escribe EXCLUIR para continuar.")
                    else:
                        res = exclude_tenant(token, t["id"], excl_reason.strip() or None)
                        if res.get("excluded"):
                            st.success("Tenant marcado como excluido.")
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

with tabs[2]:
    st.subheader("Verticals")
    st.caption("Catálogo de verticales (plantillas ADMIN) detectadas por la API.")
    if not vertical_items:
        st.warning("No se han encontrado verticales.")
    else:
        st.markdown("**Detalle de vertical**")
        selected_key = st.selectbox(
            "Selecciona un vertical",
            vertical_keys,
            format_func=lambda v: vertical_labels.get(v, v),
            key="vertical-detail-select",
        )
        if selected_key:
            detail = get_vertical(token, selected_key) or {}
            if detail.get("error"):
                st.error(detail.get("error"))
            else:
                cfg = detail.get("config") if isinstance(detail.get("config"), dict) else {}
                assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
                files = detail.get("files") if isinstance(detail.get("files"), dict) else {}
                st.markdown(f"**Key:** `{detail.get('key') or selected_key}`")
                promise = cfg.get("promise_commercial")
                if promise:
                    st.caption(f"Promesa: {promise}")
                missing = [fname for fname, ok in files.items() if not ok] if files else []
                if missing:
                    st.warning(f"Vertical incompleto (faltan: {', '.join(missing)})")
                with st.expander("metadata.json", expanded=False):
                    st.json(assets.get("metadata") or cfg or {})
                with st.expander("flow_base.json", expanded=False):
                    st.json(assets.get("flow_base") or {})
                with st.expander("semantic_schema.json", expanded=False):
                    st.json(assets.get("semantic_schema") or {})
                with st.expander("kpi_defaults.json", expanded=False):
                    st.json(assets.get("kpi_defaults") or {})
                with st.expander("prompt_vertical.txt", expanded=False):
                    st.code(assets.get("prompt_vertical") or "", language="text")
                with st.expander("prompt_vertical_extension.txt", expanded=False):
                    st.code(assets.get("prompt_vertical_extension") or "", language="text")

        st.divider()
        for v in vertical_items:
            key = v.get("key")
            label = v.get("label") or key
            with st.expander(f"{label} — {key}", expanded=False):
                promise = v.get("promise_commercial")
                if promise:
                    st.markdown(f"**Promesa comercial:** {promise}")
                st.markdown(f"**Default flow:** `{v.get('default_flow_id') or 'n/d'}`")
                ci = v.get("conversational_intelligence") or {}
                if isinstance(ci, dict) and ci:
                    st.markdown("**CI v1.1:**")
                    st.json(ci)
                scope = v.get("scope") or {}
                if isinstance(scope, dict) and scope:
                    st.markdown("**Scope:**")
                    st.json(scope)
                files = v.get("files") or {}
                if isinstance(files, dict) and files:
                    missing = [fname for fname, ok in files.items() if not ok]
                    if missing:
                        st.warning(f"Faltan archivos: {', '.join(missing)}")
                    else:
                        st.success("Archivos mínimos OK.")
                if v.get("flow_template_exists") is False:
                    st.warning("No hay flujo disponible (falta `flow_base.json` y no hay fallback en `backend/app/flows/`).")
                else:
                    st.caption(f"Fuente de flujo en runtime: `{v.get('flow_source') or 'n/d'}`")

with tabs[3]:
    st.subheader("Crear tenant")
    with st.form("create-tenant-form"):
        name = st.text_input("Nombre")
        contact = st.text_input("Email contacto")
        plan = st.selectbox("Plan", ["BASE", "PRO", "ELITE"])
        vertical_key = st.selectbox("Vertical", vertical_keys or ["kitchens"], format_func=lambda v: vertical_labels.get(v, v))
        selected_vertical = vertical_by_key.get(vertical_key) if vertical_key else None
        if isinstance(selected_vertical, dict):
            promise = selected_vertical.get("promise_commercial")
            if promise:
                st.caption(f"Promesa: {promise}")
            files = selected_vertical.get("files") or {}
            if isinstance(files, dict):
                missing = [fname for fname, ok in files.items() if not ok]
                if missing:
                    st.warning(f"Vertical incompleto (faltan: {', '.join(missing)})")
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
                "vertical_key": vertical_key,
            }
            res = create_tenant(token, payload)
            if res and "id" in res:
                st.success(f"Tenant creado: {res['id']}")
            else:
                st.error(res)
