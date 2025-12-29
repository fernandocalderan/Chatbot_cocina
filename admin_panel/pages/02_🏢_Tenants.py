import sys
from pathlib import Path

import difflib
import json

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import (
    exclude_tenant,
    get_tenant_flow,
    impersonate,
    issue_magic_link,
    issue_widget_token,
    list_tenants,
    list_tenant_flow_versions,
    publish_tenant_flow,
    revoke_widget_tokens,
    reset_tenant_flow,
    toggle_maintenance,
    update_tenant,
)
from admin_panel.ui import can_write, ensure_vertical_catalog, init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="SuperAdmin — Tenants", icon="🏢")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")


write_enabled = can_write(ctx)
if not write_enabled:
    st.info("Modo solo lectura: las acciones de escritura están desactivadas.")

if st.session_state.get("impersonation_token"):
    st.warning("Impersonación activa: bloqueando acciones de escritura para evitar errores operativos.")
    write_enabled = False

vertical_items, vertical_keys, vertical_labels, vertical_by_key = ensure_vertical_catalog(ctx)

st.title("Tenants")
st.caption("Busca y administra tenants (billing, dominios, tokens y flow).")

search_text = st.text_input(
    "Buscar tenant (email, nombre o código)",
    value="",
    placeholder="Ej: demo@kitchens.com | Demo Kitchens | OPN-000123",
)
tenants_payload = list_tenants(ctx.token, search_text.strip() or None, api_key=ctx.api_key)
tenants = tenants_payload if isinstance(tenants_payload, list) else []
_show_api_error(tenants_payload, "No se pudo cargar el listado de tenants")
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
        origins = st.text_area(
            "Allowed origins (coma)",
            value=",".join(t.get("allowed_origins") or []),
            key=f"origins-{t['id']}",
        )
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

        if st.button("Guardar", key=f"save-{t['id']}", disabled=not write_enabled):
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
            res = update_tenant(ctx.token, t["id"], payload, api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                st.error(res)
            else:
                st.success("Actualizado.")

        if st.button("ON/OFF mantenimiento", key=f"maint-{t['id']}", disabled=not write_enabled):
            res = toggle_maintenance(ctx.token, t["id"], not maint, api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                st.error(res)
            else:
                st.success(res)

        st.markdown("**Accesos y Widget**")
        col_t1, col_t2 = st.columns(2)
        allowed_origin = col_t1.text_input(
            "Dominio",
            value=(t.get("allowed_origins") or [""])[0] if t.get("allowed_origins") else "",
            key=f"allowed-origin-{t['id']}",
        )
        ttl = col_t2.slider("TTL minutos", 15, 60, 30, key=f"ttl-{t['id']}")
        if st.button("Generar token widget", key=f"token-{t['id']}", disabled=not write_enabled):
            res = issue_widget_token(ctx.token, t["id"], allowed_origin, ttl_minutes=ttl, api_key=ctx.api_key)
            if isinstance(res, dict) and "token" in res:
                st.code(res["token"], language="text")
            else:
                st.error(res)

        st.caption(f"Última revocación: {t.get('widget_tokens_revoked_before') or 'n/d'}")

        show_revoke = st.checkbox(
            "Revocar todos los tokens del widget",
            value=False,
            key=f"revoke-show-{t['id']}",
        )
        if show_revoke:
            confirm_text = st.text_input("Escribe REVOCAR para confirmar", key=f"revoke-confirm-{t['id']}")
            if st.button("Revocar tokens", key=f"revoke-{t['id']}", disabled=not write_enabled):
                if confirm_text.strip().upper() != "REVOCAR":
                    st.warning("Escribe REVOCAR para continuar.")
                else:
                    res = revoke_widget_tokens(ctx.token, t["id"], api_key=ctx.api_key)
                    if isinstance(res, dict) and "revoked_before" in res:
                        st.success(f"Revocados. Nueva marca: {res['revoked_before']}")
                    else:
                        st.error(res)

        show_magic_link = st.checkbox(
            "Magic link (acceso tenant)",
            value=False,
            key=f"ml-show-{t['id']}",
        )
        if show_magic_link:
            ml_email = st.text_input("Email destino", value=t.get("contact_email") or "", key=f"ml-email-{t['id']}")
            ml_email_clean = (ml_email or "").strip()
            if st.button(
                "Generar magic link",
                key=f"ml-btn-{t['id']}",
                disabled=(not write_enabled) or (not ml_email_clean),
            ):
                res = issue_magic_link(ctx.token, t["id"], ml_email.strip() or None, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("token"):
                    st.code(res["token"], language="text")
                    st.success(f"Enlace enviado/emitido para {res.get('email')}")
                else:
                    st.error(res)
            if not ml_email_clean:
                st.caption("Rellena un email para generar el magic link.")

        st.markdown("**Flow (estructura)**")
        show_flow_editor = st.checkbox(
            "Editar flow publicado (solo admin)",
            value=False,
            key=f"flow-edit-show-{t['id']}",
        )
        if show_flow_editor:
            st.caption("Esto cambia la estructura del flujo. Recomendado solo para soporte/ajustes avanzados.")
            state_key = f"_tenant_flow_json_{t['id']}"
            if st.button("Cargar flow", key=f"flow-load-{t['id']}"):
                out = get_tenant_flow(ctx.token, t["id"], api_key=ctx.api_key) or {}
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
            if cflow1.button("Publicar flow", key=f"flow-publish-{t['id']}", disabled=not write_enabled):
                try:
                    parsed = json.loads(flow_text or "{}")
                except Exception as exc:
                    st.error(f"JSON inválido: {exc}")
                    parsed = None
                if isinstance(parsed, dict) and parsed:
                    res = publish_tenant_flow(ctx.token, t["id"], parsed, api_key=ctx.api_key)
                    if isinstance(res, dict) and res.get("error"):
                        st.error(res)
                    else:
                        st.success(f"Publicado v{res.get('version')} ({res.get('flow_id')})")

            if cflow2.button("Reset a base del vertical", key=f"flow-reset-{t['id']}", disabled=not write_enabled):
                res = reset_tenant_flow(ctx.token, t["id"], api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success(f"Reseteado v{res.get('version')} ({res.get('flow_id')})")

            st.markdown("**Historial y rollback**")
            versions_key = f"_tenant_flow_versions_{t['id']}"
            if st.button("Cargar historial de versiones", key=f"flow-vers-load-{t['id']}"):
                versions_payload = list_tenant_flow_versions(
                    ctx.token,
                    t["id"],
                    limit=25,
                    include_schema=True,
                    api_key=ctx.api_key,
                )
                if isinstance(versions_payload, dict) and versions_payload.get("error"):
                    st.error(versions_payload)
                else:
                    st.session_state[versions_key] = versions_payload.get("items") or []

            versions = st.session_state.get(versions_key) or []
            if versions:
                options = {f"v{v.get('version')} — {v.get('published_at') or v.get('created_at') or 'n/d'}": v for v in versions}
                chosen_label = st.selectbox(
                    "Selecciona versión",
                    options=list(options.keys()),
                    key=f"flow-vers-select-{t['id']}",
                )
                chosen = options.get(chosen_label) or {}
                chosen_schema = chosen.get("schema_json") if isinstance(chosen, dict) else {}
                if not isinstance(chosen_schema, dict):
                    chosen_schema = {}

                colv1, colv2, colv3 = st.columns(3)
                if colv1.button("Cargar en editor", key=f"flow-vers-use-{t['id']}"):
                    st.session_state[state_key] = json.dumps(chosen_schema or {}, ensure_ascii=False, indent=2)
                    st.success("Versión cargada en el editor.")
                if colv2.button("Ver diff vs editor", key=f"flow-vers-diff-{t['id']}"):
                    try:
                        editor_obj = json.loads(flow_text or "{}")
                    except Exception:
                        editor_obj = {}
                    editor_norm = json.dumps(editor_obj or {}, ensure_ascii=False, indent=2, sort_keys=True).splitlines(keepends=True)
                    chosen_norm = json.dumps(chosen_schema or {}, ensure_ascii=False, indent=2, sort_keys=True).splitlines(keepends=True)
                    diff = difflib.unified_diff(
                        chosen_norm,
                        editor_norm,
                        fromfile=f"version v{chosen.get('version')}",
                        tofile="editor",
                    )
                    st.code("".join(diff) or "(sin cambios)", language="diff")
                if colv3.button(
                    "Rollback (publicar esta versión)",
                    key=f"flow-vers-rollback-{t['id']}",
                    disabled=not write_enabled,
                ):
                    if not chosen_schema:
                        st.error("La versión seleccionada no tiene schema_json.")
                    else:
                        res = publish_tenant_flow(ctx.token, t["id"], chosen_schema, api_key=ctx.api_key)
                        if isinstance(res, dict) and res.get("error"):
                            st.error(res)
                        else:
                            st.success(f"Rollback publicado v{res.get('version')} ({res.get('flow_id')})")

            show_flow_preview = st.checkbox(
                "Ver base/effective (solo lectura)",
                value=False,
                key=f"flow-view-show-{t['id']}",
            )
            if show_flow_preview:
                preview_key = f"_tenant_flow_preview_{t['id']}"
                if st.button("Cargar vista", key=f"flow-preview-{t['id']}"):
                    out = get_tenant_flow(ctx.token, t["id"], api_key=ctx.api_key) or {}
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
        show_exclude = st.checkbox(
            "Excluir tenant",
            value=False,
            key=f"exclude-show-{t['id']}",
        )
        if show_exclude:
            excl_reason = st.text_input("Motivo (opcional)", key=f"exclude-reason-{t['id']}")
            excl_confirm = st.text_input("Escribe EXCLUIR para confirmar", key=f"exclude-confirm-{t['id']}")
            if st.button("Excluir tenant", key=f"exclude-{t['id']}", disabled=not write_enabled):
                if excl_confirm.strip().upper() != "EXCLUIR":
                    st.warning("Escribe EXCLUIR para continuar.")
                else:
                    res = exclude_tenant(ctx.token, t["id"], excl_reason.strip() or None, api_key=ctx.api_key)
                    if isinstance(res, dict) and res.get("excluded"):
                        st.success("Tenant marcado como excluido.")
                    else:
                        st.error(res)

        if st.button("Impersonar", key=f"imp-{t['id']}", disabled=not write_enabled):
            res = impersonate(ctx.token, t["id"], api_key=ctx.api_key)
            if isinstance(res, dict) and "token" in res:
                st.session_state["impersonation_token"] = res["token"]
                st.code(res["token"], language="text")
                st.info("Impersonación almacenada en sesión local. Úsalo en el panel de tenant o sal para limpiar.")
            else:
                st.error(res)
