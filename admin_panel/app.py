import os
import json
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
    get_tenant_flow,
    issue_magic_link,
    list_tenants,
    list_verticals,
    publish_tenant_flow,
    reset_tenant_flow,
    resolve_admin_api_key,
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

with st.sidebar:
    st.page_link("app.py", label="Inicio", icon="🏠")
    st.page_link("pages/widget_tester.py", label="Widget tester 💬", icon="🧪")

admin_api_key = resolve_admin_api_key()


def _show_api_error(payload: object, fallback: str = "Error llamando a la API") -> bool:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")
        return True
    return False

with st.sidebar:
    if admin_api_key:
        st.success("Autenticado con ADMIN_API_KEY/ADMIN_API_TOKEN (bypass OIDC).")
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

vertical_payload = list_verticals(token, api_key=api_key) or {}
_show_api_error(vertical_payload, fallback="No se pudo cargar el catálogo de verticales")
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
    ov = admin_overview(token, api_key=api_key) or {}
    _show_api_error(ov, fallback="No se pudo cargar el overview")
    tenants_payload = list_tenants(token, api_key=api_key)
    tenants = tenants_payload if isinstance(tenants_payload, list) else []
    _show_api_error(tenants_payload, fallback="No se pudo cargar el listado de tenants")
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
        err_payload = admin_recent_errors(token, api_key=api_key) or {}
        _show_api_error(err_payload, fallback="No se pudieron cargar errores recientes")
        errs = err_payload.get("items") or []
        if errs:
            for err in errs[:5]:
                st.markdown(f"- {err.get('timestamp', '')} — {err.get('level', '')}: {err.get('message')}")
            if len(errs) > 5:
                st.caption(f"... y {len(errs)-5} más")
        else:
            st.info("Sin errores recientes")

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    health = admin_health(token, api_key=api_key) or {}
    _show_api_error(health, fallback="No se pudo cargar el estado de health")
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
        alert_payload = admin_alerts(token, api_key=api_key) or {}
        _show_api_error(alert_payload, fallback="No se pudieron cargar alertas")
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
    tenants_payload = list_tenants(token, search_text.strip() or None, api_key=api_key)
    tenants = tenants_payload if isinstance(tenants_payload, list) else []
    _show_api_error(tenants_payload, fallback="No se pudo cargar el listado de tenants")
    st.caption(f"Resultados: {len(tenants)}")

    for t in tenants:
        code = t.get("customer_code") or "N/D"
        with st.expander(f"{t.get('name')} — {t.get('plan')} — {code} — {t.get('id')}"):
            st.text_input("Código comercial", value=code, disabled=True, key=f"code-{t['id']}")

            st.markdown("**Contacto y dirección**")
            c1, c2 = st.columns(2)
            contact_email = c1.text_input(
                "Email de contacto",
                value=t.get("contact_email") or "",
                key=f"contact-email-{t['id']}",
            )
            contact_phone = c2.text_input(
                "Teléfono de contacto",
                value=t.get("contact_phone") or "",
                key=f"contact-phone-{t['id']}",
            )
            a1, a2, a3, a4 = st.columns(4)
            address_street = a1.text_input(
                "Calle/Av",
                value=t.get("address_street") or "",
                key=f"addr-street-{t['id']}",
            )
            address_number = a2.text_input(
                "Número",
                value=t.get("address_number") or "",
                key=f"addr-number-{t['id']}",
            )
            address_postal = a3.text_input(
                "Código postal",
                value=t.get("address_postal_code") or "",
                key=f"addr-postal-{t['id']}",
            )
            address_city = a4.text_input(
                "Población",
                value=t.get("address_city") or "",
                key=f"addr-city-{t['id']}",
            )

            if vertical_keys:
                current_vertical = t.get("vertical_key") or vertical_keys[0]
                st.text_input(
                    "Vertical actual",
                    value=vertical_labels.get(current_vertical, current_vertical),
                    disabled=True,
                    key=f"vertical-label-{t['id']}",
                )
                scope_items = (vertical_by_key.get(current_vertical) or {}).get("scope_items") or []
                scope_labels = {
                    str(it.get("key")): (it.get("label") or it.get("key"))
                    for it in scope_items
                    if isinstance(it, dict) and it.get("key")
                }
                scope_keys = list(scope_labels.keys())
                current_scopes = t.get("vertical_scopes") or []
                if scope_keys:
                    selected_scopes = st.multiselect(
                        "Scopes (sub-verticals)",
                        scope_keys,
                        default=[s for s in current_scopes if s in scope_keys] or [],
                        format_func=lambda k: scope_labels.get(k, k),
                        key=f"scopes-{t['id']}",
                        help="Selecciona 1 o más scopes para alinear el flujo base del vertical.",
                    )
                else:
                    selected_scopes = []
            else:
                current_vertical = None
                selected_scopes = []

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
            custom_flow_enabled = st.checkbox(
                "Flujo personalizado activo",
                value=bool(t.get("custom_flow_enabled") or False),
                key=f"custom-flow-enabled-{t['id']}",
                help="Si está desactivado, el widget usa el flujo base (vertical + scopes). Si está activado, usa el flow publicado.",
            )
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
                    "contact_email": contact_email.strip() or None,
                    "contact_phone": contact_phone.strip() or None,
                    "address_street": address_street.strip() or None,
                    "address_number": address_number.strip() or None,
                    "address_postal_code": address_postal.strip() or None,
                    "address_city": address_city.strip() or None,
                    "plan": new_plan,
                    "ia_monthly_limit_eur": new_limit,
                    "allowed_origins": [o.strip() for o in origins.split(",") if o.strip()],
                    "maintenance": maint,
                    "ia_enabled": use_ia,
                    "use_ia": use_ia,
                    "billing_status": billing_status,
                    "vertical_scopes": selected_scopes,
                    "custom_flow_enabled": custom_flow_enabled,
                }
                if new_vertical and new_vertical != current_vertical:
                    payload["vertical_key"] = new_vertical
                    payload["force_vertical"] = force_vertical
                res = update_tenant(token, t["id"], payload, api_key=api_key)
                st.success(f"Actualizado: {res}")
            if st.button("ON/OFF mantenimiento", key=f"maint-{t['id']}"):
                res = toggle_maintenance(token, t["id"], not maint, api_key=api_key)
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
                res = issue_widget_token(token, t["id"], allowed_origin, ttl_minutes=ttl, api_key=api_key)
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
                        res = revoke_widget_tokens(token, t["id"], api_key=api_key)
                        if "revoked_before" in res:
                            st.success(f"Revocados. Nueva marca: {res['revoked_before']}")
                        else:
                            st.error(res)
            with st.expander("Magic link (acceso tenant)", expanded=False):
                ml_email = st.text_input("Email destino", value=t.get("contact_email") or "", key=f"ml-email-{t['id']}")
                ml_email_clean = (ml_email or "").strip()
                if st.button("Generar magic link", key=f"ml-btn-{t['id']}", disabled=not ml_email_clean):
                    res = issue_magic_link(token, t["id"], ml_email.strip() or None, api_key=api_key)
                    if res.get("token"):
                        st.code(res["token"], language="text")
                        st.success(f"Enlace enviado/emitido para {res.get('email')}")
                    else:
                        if (
                            isinstance(res.get("error"), str)
                            and res.get("status_code") == 400
                            and "missing_email" in res.get("error", "")
                        ):
                            st.warning("Falta el email. Rellena “Email destino” o guarda un email de contacto en el tenant.")
                        else:
                            st.error(res)
                if not ml_email_clean:
                    st.caption("Rellena un email para generar el magic link.")

            st.markdown("**Flow (estructura)**")
            with st.expander("Editar flow publicado (solo admin)", expanded=False):
                st.caption("Esto cambia la estructura del flujo. Recomendado solo para soporte/ajustes avanzados.")
                state_key = f"_tenant_flow_json_{t['id']}"
                if st.button("Cargar flow", key=f"flow-load-{t['id']}"):
                    out = get_tenant_flow(token, t["id"], api_key=api_key) or {}
                    if out.get("error"):
                        st.error(out)
                    else:
                        flow_obj = out.get("custom_flow") if isinstance(out, dict) else {}
                        st.session_state[state_key] = json.dumps(flow_obj or {}, ensure_ascii=False, indent=2)
                        st.success("Flujo personalizado cargado en el editor.")
                flow_text = st.text_area(
                    "Flow JSON",
                    value=st.session_state.get(state_key) or "{}",
                    height=260,
                    key=f"flow-json-area-{t['id']}",
                )
                cflow1, cflow2 = st.columns(2)
                if cflow1.button("Publicar flow", key=f"flow-publish-{t['id']}"):
                    try:
                        parsed = json.loads(flow_text or "{}")
                    except Exception as exc:
                        st.error(f"JSON inválido: {exc}")
                        parsed = None
                    if isinstance(parsed, dict) and parsed:
                        res = publish_tenant_flow(token, t["id"], parsed, api_key=api_key)
                        if res.get("error"):
                            st.error(res)
                        else:
                            st.success(f"Publicado v{res.get('version')} ({res.get('flow_id')})")
                if cflow2.button("Reset a base del vertical", key=f"flow-reset-{t['id']}"):
                    res = reset_tenant_flow(token, t["id"], api_key=api_key)
                    if res.get("error"):
                        st.error(res)
                    else:
                        st.success(f"Reseteado v{res.get('version')} ({res.get('flow_id')})")

                with st.expander("Ver base/effective (solo lectura)", expanded=False):
                    preview_key = f"_tenant_flow_preview_{t['id']}"
                    if st.button("Cargar vista", key=f"flow-preview-{t['id']}"):
                        out = get_tenant_flow(token, t["id"], api_key=api_key) or {}
                        st.session_state[preview_key] = out
                    out = st.session_state.get(preview_key) or {}
                    if not out:
                        st.caption("Pulsa “Cargar vista” para ver base/effective.")
                    elif out.get("error"):
                        st.error(out)
                    else:
                        st.caption(
                            f"custom_flow_enabled={bool(out.get('custom_flow_enabled'))} | scopes={out.get('scopes') or []}"
                        )
                        st.markdown("**Base flow (vertical + scopes)**")
                        st.json(out.get("base_flow") or {})
                        st.markdown("**Effective flow (lo que usa el widget)**")
                        st.json(out.get("effective_flow") or {})

            st.markdown("**Estado y seguridad**")
            with st.expander("Excluir tenant", expanded=False):
                excl_reason = st.text_input("Motivo (opcional)", key=f"exclude-reason-{t['id']}")
                excl_confirm = st.text_input("Escribe EXCLUIR para confirmar", key=f"exclude-confirm-{t['id']}")
                if st.button("Excluir tenant", key=f"exclude-{t['id']}"):
                    if excl_confirm.strip().upper() != "EXCLUIR":
                        st.warning("Escribe EXCLUIR para continuar.")
                    else:
                        res = exclude_tenant(token, t["id"], excl_reason.strip() or None, api_key=api_key)
                        if res.get("excluded"):
                            st.success("Tenant marcado como excluido.")
                        else:
                            st.error(res)

            if st.button("Impersonar", key=f"imp-{t['id']}"):
                res = impersonate(token, t["id"], api_key=api_key)
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
            detail = get_vertical(token, selected_key, api_key=api_key) or {}
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
    st.caption("Los campos de vertical/scopes se actualizan automáticamente (sin form) para evitar problemas de cascada.")
    col_a, col_b = st.columns(2)
    with col_a:
        name = st.text_input("Nombre comercial", key="ct-name")
        contact = st.text_input("Email de contacto", key="ct-email")
        phone = st.text_input("Teléfono de contacto", key="ct-phone")
        plan = st.selectbox("Plan", ["BASE", "PRO", "ELITE"], key="ct-plan")
        vertical_key = st.selectbox(
            "Vertical",
            vertical_keys or ["kitchens"],
            format_func=lambda v: vertical_labels.get(v, v),
            key="ct-vertical",
        )
    with col_b:
        st.markdown("**Dirección completa**")
        addr_street = st.text_input("Calle/Av", key="ct-addr-street")
        addr_number = st.text_input("Número", key="ct-addr-number")
        addr_postal = st.text_input("Código postal", key="ct-addr-postal")
        addr_city = st.text_input("Población", key="ct-addr-city")
        origins_new = st.text_input("Allowed origins (coma)", key="ct-origins")
        limit = st.number_input("Límite IA €", min_value=0.0, step=5.0, value=0.0, key="ct-limit")
        maint_new = st.checkbox("Mantenimiento inicial", value=False, key="ct-maint")
        use_ia_new = st.checkbox("IA habilitada", value=True, key="ct-ia")

    selected_scopes_new: list[str] = []
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
        scope_items = selected_vertical.get("scope_items") or []
        scope_labels = {
            str(it.get("key")): (it.get("label") or it.get("key"))
            for it in scope_items
            if isinstance(it, dict) and it.get("key")
        }
        scope_keys = list(scope_labels.keys())
        if scope_keys:
            st.caption("Selecciona 1 o más scopes (sub-verticals) — opciones dependen del vertical.")
            scopes_key = f"ct-scopes-{vertical_key}"
            selected_scopes_new = st.multiselect(
                "Scopes (sub-verticals)",
                scope_keys,
                default=st.session_state.get(scopes_key) or [scope_keys[0]],
                format_func=lambda k: scope_labels.get(k, k),
                key=scopes_key,
            )

    if st.button("Crear", use_container_width=True, key="ct-submit"):
        payload = {
            "name": name,
            "contact_email": contact or None,
            "contact_phone": phone or None,
            "address_street": addr_street or None,
            "address_number": addr_number or None,
            "address_postal_code": addr_postal or None,
            "address_city": addr_city or None,
            "plan": plan,
            "ia_monthly_limit_eur": limit,
            "allowed_origins": [o.strip() for o in origins_new.split(",") if o.strip()],
            "maintenance": maint_new,
            "use_ia": use_ia_new,
            "ia_enabled": use_ia_new,
            "vertical_key": vertical_key,
            "vertical_scopes": selected_scopes_new,
        }
        res = create_tenant(token, payload, api_key=api_key)
        if res and "id" in res:
            st.success(f"Tenant creado: {res['id']}")
        else:
            st.error(res)
