import sys
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import (
    exclude_tenant,
    get_catalog,
    get_published_flow,
    get_tenant_flow,
    include_tenant,
    import_flow_base,
    issue_widget_token,
    list_tenants,
    publish_flow,
    publish_flow_by_id,
    reset_sessions,
    tenant_flow_diff,
    tenant_flow_publish_override,
    tenant_flow_sync,
    toggle_maintenance,
    update_tenant,
)
from admin_panel.ui import (
    can_write,
    ensure_vertical_catalog,
    init_page,
    pill,
    render_impersonation_banner,
    render_sidebar_nav,
    require_admin_context,
)

init_page(title="SuperAdmin — Tenants", icon="🏢")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

write_enabled = can_write(ctx) and not st.session_state.get("impersonation_token")
if not write_enabled:
    st.info("Modo solo lectura o impersonación: acciones de escritura desactivadas.")

vertical_items, vertical_keys, vertical_labels, vertical_by_key = ensure_vertical_catalog(ctx)

st.title("Tenants")
st.caption("Sencillo v2: plan + permisos IA + vertical/scopes + flow publicado + widget token.")


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")


search_text = st.text_input(
    "Buscar tenant (email, nombre o código)",
    value="",
    placeholder="Ej: demo@example.com | Demo Studio | OPN-000123",
)
tenants_payload = list_tenants(ctx.token, search_text.strip() or None, api_key=ctx.api_key)
tenants = tenants_payload if isinstance(tenants_payload, list) else []
_show_api_error(tenants_payload, "No se pudo cargar el listado de tenants")
st.caption(f"Resultados: {len(tenants)}")


def _scopes_for_vertical(vkey: str | None) -> tuple[list[str], dict[str, str]]:
    if not vkey:
        return [], {}
    v = vertical_by_key.get(vkey) if isinstance(vertical_by_key, dict) else None
    scope_items = (v or {}).get("scope_items") or []
    labels = {
        str(it.get("key")): (it.get("label") or it.get("key"))
        for it in scope_items
        if isinstance(it, dict) and it.get("key")
    }
    keys = list(labels.keys())
    return keys, labels


def _tenant_scope_rows(catalog: dict, vertical_key: str | None) -> list[dict]:
    rows: list[dict] = []
    for v in catalog.get("verticals") or []:
        if vertical_key and v.get("vertical_key") != vertical_key:
            continue
        for s in v.get("scopes") or []:
            flows = s.get("flows") or []
            tenant_flows = [f for f in flows if str(f.get("owner_type") or "").upper() == "TENANT"]
            published_count = len([f for f in tenant_flows if f.get("published")])
            if not tenant_flows:
                status = "NO_FLOW_YET"
            elif published_count > 1:
                status = "MULTIPLE_PUBLISHED"
            elif published_count == 1:
                status = "PUBLISHED_OK"
            else:
                status = "DRAFT_ONLY"
            rows.append(
                {
                    "vertical_key": v.get("vertical_key"),
                    "scope_key": s.get("scope_key"),
                    "status": status,
                    "flows_count": len(tenant_flows),
                    "published_count": published_count,
                    "has_fs_def": bool(s.get("has_filesystem_definition")),
                    "source": s.get("source"),
                    "flows": tenant_flows,
                }
            )
    return rows


for t in tenants:
    tenant_id = t.get("id")
    if not tenant_id:
        continue
    name = t.get("name") or tenant_id
    plan = t.get("plan") or "BASE"
    code = t.get("customer_code") or "—"

    scopes_current = t.get("vertical_scopes") or []
    tenant_vertical = t.get("vertical_key")
    tenant_vertical_missing = not (tenant_vertical and str(tenant_vertical).strip())
    v_current = tenant_vertical or (vertical_keys[0] if vertical_keys else None)
    flow_system = str(t.get("flow_system") or "v2").strip().lower()
    if flow_system != "v2":
        flow_system = "v2"

    ia_enabled = bool(t.get("ia_enabled", False)) and bool(t.get("use_ia", False))
    excluded = bool(t.get("excluded") or False)
    excl_tag = " — EXCLUIDO" if excluded else ""
    with st.expander(f"{name} — {plan} — {code} — {tenant_id}{excl_tag}", expanded=False):
        tab_cfg, tab_ia, tab_widget = st.tabs(["Config", "Plan & IA", "Widget & Flow"])

        with tab_cfg:
            c1, c2 = st.columns(2)
            contact_email = c1.text_input("Email", value=t.get("contact_email") or "", key=f"email-{tenant_id}")
            contact_phone = c2.text_input("Teléfono", value=t.get("contact_phone") or "", key=f"phone-{tenant_id}")

            a1, a2, a3, a4 = st.columns(4)
            address_street = a1.text_input("Calle/Av", value=t.get("address_street") or "", key=f"street-{tenant_id}")
            address_number = a2.text_input("Número", value=t.get("address_number") or "", key=f"number-{tenant_id}")
            address_postal = a3.text_input("CP", value=t.get("address_postal_code") or "", key=f"cp-{tenant_id}")
            address_city = a4.text_input("Ciudad", value=t.get("address_city") or "", key=f"city-{tenant_id}")

            st.markdown("**Vertical y scopes**")
            colv1, colv2 = st.columns([0.7, 0.3])
            new_vertical = colv1.selectbox(
                "Vertical",
                options=vertical_keys or [],
                index=(vertical_keys.index(v_current) if v_current in vertical_keys else 0) if vertical_keys else 0,
                format_func=lambda v: vertical_labels.get(v, v),
                key=f"vertical-{tenant_id}",
                disabled=not write_enabled,
            )
            force_vertical = colv2.checkbox(
                "Forzar cambio",
                value=False,
                key=f"force-vertical-{tenant_id}",
                disabled=not write_enabled,
                help="Si el vertical ya estaba definido, el cambio requiere forzar.",
            )
            scope_keys, scope_labels = _scopes_for_vertical(new_vertical)
            primary_scope = ""
            extra_scopes: list[str] = []
            if scope_keys:
                current_primary = scopes_current[0] if scopes_current else scope_keys[0]
                primary_scope = st.selectbox(
                    "Scope principal (estructura del flow)",
                    options=scope_keys,
                    index=scope_keys.index(current_primary) if current_primary in scope_keys else 0,
                    format_func=lambda k: scope_labels.get(k, k),
                    key=f"scope-primary-{tenant_id}",
                    disabled=not write_enabled,
                )
                extra_scopes = st.multiselect(
                    "Scopes adicionales (influyen en prompts/KB)",
                    options=scope_keys,
                    default=[s for s in scopes_current[1:] if s in scope_keys],
                    format_func=lambda k: scope_labels.get(k, k),
                    key=f"scope-extra-{tenant_id}",
                    disabled=not write_enabled,
                )
            combined_scopes = []
            if primary_scope:
                combined_scopes.append(primary_scope)
            combined_scopes.extend([s for s in extra_scopes if s and s != primary_scope])

        with tab_ia:
            st.markdown("**Plan**")
            new_plan = st.selectbox(
                "Plan",
                ["BASE", "PRO", "ELITE"],
                index=["BASE", "PRO", "ELITE"].index(plan) if plan in {"BASE", "PRO", "ELITE"} else 0,
                key=f"plan-{tenant_id}",
                disabled=not write_enabled,
            )
            st.markdown("**Permisos IA (builder + KB)**")
            ia_toggle = st.checkbox(
                "IA habilitada (permiso)",
                value=ia_enabled,
                key=f"ia-{tenant_id}",
                disabled=not write_enabled,
                help="Habilita embeddings (KB) + generación de textos del flow (cuota por plan).",
            )
            limit = st.number_input(
                "Override límite IA € (0 = usar plan)",
                min_value=0.0,
                step=5.0,
                value=float(t.get("ia_monthly_limit_eur") or 0.0),
                key=f"ia-limit-{tenant_id}",
                disabled=not write_enabled,
            )

            billing_status = st.selectbox(
                "Billing status",
                ["ACTIVE", "PAST_DUE", "CANCELED", "INCOMPLETE"],
                index=["ACTIVE", "PAST_DUE", "CANCELED", "INCOMPLETE"].index(str(t.get("billing_status") or "ACTIVE")),
                key=f"billing-{tenant_id}",
                disabled=not write_enabled,
            )
            maintenance = st.checkbox(
                "Mantenimiento",
                value=bool(t.get("maintenance") or False),
                key=f"maint-{tenant_id}",
                disabled=not write_enabled,
            )
            st.divider()
            st.markdown("**Exclusión (bloqueo total)**")
            if excluded:
                st.warning("Tenant excluido: se bloquea panel/widget/runtime. Solo admin puede gestionarlo.")
                st.caption(f"Motivo: {t.get('excluded_reason') or '—'}")
            else:
                st.caption("Excluye un tenant para bloquearlo completamente (DB).")
            excl_reason = st.text_input(
                "Motivo (opcional)",
                value="",
                key=f"exclude-reason-{tenant_id}",
                disabled=not write_enabled,
            )
            cex1, cex2 = st.columns(2)
            if write_enabled and cex1.button(
                "Excluir tenant",
                key=f"exclude-{tenant_id}",
                use_container_width=True,
                disabled=excluded,
            ):
                res = exclude_tenant(ctx.token, tenant_id, reason=excl_reason.strip() or None, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Tenant excluido.")
                    st.rerun()
            if write_enabled and cex2.button(
                "Reactivar tenant",
                key=f"include-{tenant_id}",
                use_container_width=True,
                disabled=not excluded,
            ):
                res = include_tenant(ctx.token, tenant_id, reason=excl_reason.strip() or None, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Tenant reactivado (IA sigue según permisos).")
                    st.rerun()
            if write_enabled and st.button("Guardar (config + plan + IA)", key=f"save-{tenant_id}", use_container_width=True):
                payload = {
                    "contact_email": contact_email.strip() or None,
                    "contact_phone": contact_phone.strip() or None,
                    "address_street": address_street.strip() or None,
                    "address_number": address_number.strip() or None,
                    "address_postal_code": address_postal.strip() or None,
                    "address_city": address_city.strip() or None,
                    "plan": new_plan,
                    "ia_enabled": ia_toggle,
                    "use_ia": ia_toggle,
                    "ia_monthly_limit_eur": None if float(limit or 0.0) <= 0 else float(limit),
                    "billing_status": billing_status,
                    "maintenance": bool(maintenance),
                    "vertical_scopes": combined_scopes,
                    "flow_system": "v2",
                }
                if new_vertical and new_vertical != v_current:
                    payload["vertical_key"] = new_vertical
                    payload["force_vertical"] = bool(force_vertical)
                res = update_tenant(ctx.token, tenant_id, payload, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Actualizado.")
                    st.rerun()

            if write_enabled and st.button("ON/OFF mantenimiento", key=f"toggle-maint-{tenant_id}", use_container_width=True):
                res = toggle_maintenance(ctx.token, tenant_id, not bool(t.get("maintenance") or False), api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("OK")
                    st.rerun()

        with tab_widget:
            st.markdown("**Widget token**")
            allowed_origins = t.get("allowed_origins") or []
            origins = st.text_area(
                "Allowed origins (coma)",
                value=",".join(allowed_origins),
                key=f"origins-{tenant_id}",
                disabled=not write_enabled,
            )
            colw1, colw2 = st.columns([0.65, 0.35])
            allowed_origin = colw1.text_input(
                "Dominio para token",
                value=(allowed_origins[0] if allowed_origins else ""),
                key=f"origin-{tenant_id}",
                disabled=not write_enabled,
            )
            ttl = colw2.slider("TTL minutos", 15, 60, 30, key=f"ttl-{tenant_id}", disabled=not write_enabled)
            if write_enabled and st.button("Guardar origins", key=f"save-origins-{tenant_id}", use_container_width=True):
                new_list = [o.strip() for o in origins.split(",") if o.strip()]
                res = update_tenant(ctx.token, tenant_id, {"allowed_origins": new_list}, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("OK")
                    st.rerun()
            if write_enabled and st.button("Generar token widget", key=f"gen-token-{tenant_id}", use_container_width=True):
                res = issue_widget_token(ctx.token, tenant_id, allowed_origin, ttl_minutes=int(ttl), api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("token"):
                    st.code(res["token"], language="text")
                else:
                    st.error(res)

            st.divider()
            st.markdown("**Flow efectivo**")
            debug_mode = bool(st.session_state.get("debug"))
            if debug_mode:
                st.caption(f"Tenant activo: `{tenant_id}`")
            if not v_current:
                st.warning("Tenant sin vertical_key: no se puede resolver catálogo de scopes.")
            catalog_payload = get_catalog(
                ctx.token,
                vertical_key=v_current if v_current else None,
                tenant_id=tenant_id,
                include_empty_scopes=True,
                include_drafts=True,
                include_templates=True,
                api_key=ctx.api_key,
            )
            if isinstance(catalog_payload, dict) and catalog_payload.get("error"):
                st.error(catalog_payload)
                catalog_payload = {}
            scope_rows = _tenant_scope_rows(catalog_payload or {}, v_current if v_current else None)
            if scope_rows:
                st.markdown("**Scopes del tenant**")
                c1, c2, c3, c4, c5 = st.columns([0.34, 0.16, 0.16, 0.16, 0.18])
                c1.caption("Scope")
                c2.caption("Estado")
                c3.caption("Flows")
                c4.caption("Publicado")
                c5.caption("Acción")
                for row in sorted(scope_rows, key=lambda r: str(r.get("scope_key") or "")):
                    status = row.get("status") or "NO_FLOW_YET"
                    tone = "info"
                    if status == "PUBLISHED_OK":
                        tone = "success"
                    elif status == "DRAFT_ONLY":
                        tone = "warning"
                    elif status == "MULTIPLE_PUBLISHED":
                        tone = "danger"
                    badge = pill(status, tone)
                    cc1, cc2, cc3, cc4, cc5 = st.columns([0.34, 0.16, 0.16, 0.16, 0.18])
                    cc1.markdown(f"**{row.get('scope_key')}**")
                    cc2.markdown(badge, unsafe_allow_html=True)
                    cc3.write(str(row.get("flows_count") or 0))
                    cc4.write(str(row.get("published_count") or 0))
                    action_label = "Ver"
                    if status == "NO_FLOW_YET":
                        action_label = "Subir flow base"
                    elif status == "DRAFT_ONLY":
                        action_label = "Publicar"
                    action_key = f"scope-action-{tenant_id}-{row.get('scope_key')}"
                    disabled_action = not write_enabled or not v_current
                    clicked = cc5.button(
                        action_label,
                        key=action_key,
                        disabled=disabled_action,
                        help=None,
                        use_container_width=True,
                    )
                    if clicked:
                        st.session_state[action_key] = True
                    if st.session_state.get(action_key):
                        if status == "NO_FLOW_YET":
                            with st.expander(f"Subir flow base ({row.get('scope_key')})", expanded=True):
                                up = st.file_uploader(
                                    "Flow base JSON",
                                    type=["json"],
                                    key=f"upload-{tenant_id}-{row.get('scope_key')}",
                                )
                                confirm_import = st.checkbox(
                                    "Importar como draft",
                                    value=False,
                                    key=f"confirm-import-{tenant_id}-{row.get('scope_key')}",
                                )
                                if st.button(
                                    "Importar",
                                    key=f"do-import-{tenant_id}-{row.get('scope_key')}",
                                    disabled=not (up and confirm_import and v_current),
                                ):
                                    res = import_flow_base(
                                        ctx.token,
                                        file_name=up.name,
                                        file_bytes=up.getvalue(),
                                        vertical_key=v_current or "",
                                        scope_key=row.get("scope_key") or "",
                                        owner_type="TENANT",
                                        owner_id=tenant_id,
                                        api_key=ctx.api_key,
                                    )
                                    if isinstance(res, dict) and res.get("error"):
                                        st.error(res)
                                    else:
                                        st.success("Flow base importado como draft.")
                                        st.rerun()
                        elif status == "DRAFT_ONLY":
                            drafts = [f for f in row.get("flows") or [] if not f.get("published")]
                            drafts_sorted = sorted(drafts, key=lambda f: int(f.get("version") or 0), reverse=True)
                            latest = drafts_sorted[0] if drafts_sorted else None
                            with st.expander(f"Publicar ({row.get('scope_key')})", expanded=True):
                                if latest:
                                    st.caption(f"Draft v{latest.get('version')} · {latest.get('flow_id')}")
                                pub_confirm = st.checkbox(
                                    "Confirmo que quiero publicar este flow y despublicar versiones anteriores.",
                                    value=False,
                                    key=f"confirm-pub-{tenant_id}-{row.get('scope_key')}",
                                )
                                pub_text = st.text_input(
                                    "Escribe PUBLICAR para habilitar",
                                    value="",
                                    key=f"confirm-pub-text-{tenant_id}-{row.get('scope_key')}",
                                )
                                can_pub = pub_confirm and pub_text.strip().lower() == "publicar"
                                if st.button(
                                    "Publicar",
                                    key=f"do-pub-{tenant_id}-{row.get('scope_key')}",
                                    disabled=not (latest and can_pub),
                                ):
                                    res = publish_flow_by_id(
                                        ctx.token,
                                        flow_id=str(latest.get("flow_id")),
                                        api_key=ctx.api_key,
                                    )
                                    if isinstance(res, dict) and res.get("error"):
                                        st.error(res)
                                    else:
                                        st.success("Flow publicado.")
                                        st.rerun()
                        else:
                            with st.expander(f"Ver flow ({row.get('scope_key')})", expanded=False):
                                published = [f for f in row.get("flows") or [] if f.get("published")]
                                if published:
                                    p = sorted(published, key=lambda f: int(f.get("version") or 0), reverse=True)[0]
                                    st.write(f"Publicado v{p.get('version')} · {p.get('published_at') or '—'}")
                                    if debug_mode:
                                        st.caption(f"id: {p.get('flow_id')}")
                    if debug_mode:
                        flow_ids = [f.get("flow_id") for f in row.get("flows") or [] if f.get("flow_id")]
                        if flow_ids:
                            cc1.caption(f"flows: {', '.join(flow_ids)}")
                        if row.get("source") == "DB_ONLY" or not row.get("has_fs_def"):
                            cc2.caption("warning: scope sin definición FS")
                st.divider()
                st.markdown("**Plantilla y Sync (override)**")
                if tenant_vertical_missing:
                    st.warning(
                        "Este tenant no tiene `vertical_key` configurado. "
                        "Sync/Publish deshabilitados hasta asignar un vertical."
                    )
                for row in sorted(scope_rows, key=lambda r: str(r.get("scope_key") or "")):
                    skey = row.get("scope_key") or ""
                    diff_state_key = f"diff-{tenant_id}-{skey}"
                    with st.expander(f"{skey} · Sync", expanded=False):
                        col_a, col_b = st.columns([0.5, 0.5])
                        if col_a.button(
                            "Ver diff",
                            key=f"diff-btn-{tenant_id}-{skey}",
                            use_container_width=True,
                            disabled=tenant_vertical_missing,
                        ):
                            diff_res = tenant_flow_diff(
                                ctx.token,
                                tenant_id,
                                vertical_key=tenant_vertical or "",
                                scope_key=skey,
                                flow_kind="base",
                                api_key=ctx.api_key,
                            )
                            st.session_state[diff_state_key] = diff_res
                        diff_data = st.session_state.get(diff_state_key)
                        if isinstance(diff_data, dict) and diff_data.get("error"):
                            st.error(diff_data)
                        elif isinstance(diff_data, dict) and diff_data:
                            st.caption(
                                f"Base v{diff_data.get('base_version')} · base_flow_id={diff_data.get('base_flow_id')}"
                            )
                            st.caption(
                                f"Override: {diff_data.get('override_flow_id') or '—'} · "
                                f"published={diff_data.get('override_published')} · "
                                f"updated_at={diff_data.get('override_updated_at') or '—'}"
                            )
                            diff_counts = diff_data.get("diff") or {}
                            st.write(
                                {
                                    "changed": len(diff_counts.get("changed") or []),
                                    "added": len(diff_counts.get("added") or []),
                                    "removed": len(diff_counts.get("removed") or []),
                                }
                            )
                            if debug_mode:
                                st.json(diff_counts)

                        with col_b:
                            sync_confirm = st.checkbox(
                                "Confirmo sync desde plantilla",
                                value=False,
                                key=f"sync-confirm-{tenant_id}-{skey}",
                            )
                            sync_text = st.text_input(
                                "Escribe SYNC para habilitar",
                                value="",
                                key=f"sync-text-{tenant_id}-{skey}",
                            )
                            can_sync = sync_confirm and sync_text.strip().lower() == "sync"
                            if st.button(
                                "Sync now",
                                key=f"sync-btn-{tenant_id}-{skey}",
                                disabled=not can_sync or tenant_vertical_missing,
                                use_container_width=True,
                            ):
                                res = tenant_flow_sync(
                                    ctx.token,
                                    tenant_id,
                                    vertical_key=tenant_vertical or "",
                                    scope_key=skey,
                                    flow_kind="base",
                                    api_key=ctx.api_key,
                                )
                                if isinstance(res, dict) and res.get("error"):
                                    st.error(res)
                                else:
                                    st.success("Override creado/actualizado como borrador.")
                                    st.session_state.pop(diff_state_key, None)
                                    st.rerun()

                        pub_confirm = st.checkbox(
                            "Confirmo publicación del override",
                            value=False,
                            key=f"ov-pub-confirm-{tenant_id}-{skey}",
                        )
                        pub_text = st.text_input(
                            "Escribe PUBLICAR para habilitar",
                            value="",
                            key=f"ov-pub-text-{tenant_id}-{skey}",
                        )
                        can_pub = pub_confirm and pub_text.strip().lower() == "publicar"
                        if st.button(
                            "Publicar override",
                            key=f"ov-pub-btn-{tenant_id}-{skey}",
                            disabled=not can_pub or tenant_vertical_missing,
                            use_container_width=True,
                        ):
                            res = tenant_flow_publish_override(
                                ctx.token,
                                tenant_id,
                                vertical_key=tenant_vertical or "",
                                scope_key=skey,
                                flow_kind="base",
                                published=True,
                                api_key=ctx.api_key,
                            )
                            if isinstance(res, dict) and res.get("error"):
                                st.error(res)
                            else:
                                st.success("Override publicado.")
                                st.session_state.pop(diff_state_key, None)
                                st.rerun()
            else:
                st.caption("Sin scopes detectados para este tenant.")
            health_check = get_published_flow(ctx.token, tenant_id, api_key=ctx.api_key)
            health_status = str(health_check.get("status") or "ERROR")
            if health_status == "OK":
                st.success("✅ Backend resolverá este flow publicado.")
            elif health_status == "NO_PUBLISHED":
                st.warning("⚠️ Chat responderá 409 hasta publicar.")
            elif health_status == "MULTIPLE_PUBLISHED":
                st.error("❌ Inconsistencia: corregir antes de operar.")
            else:
                if isinstance(health_check, dict) and health_check.get("error"):
                    st.warning(f"Health check: {health_check.get('error')}")
            with st.spinner("Cargando flow…"):
                flow_info = get_tenant_flow(ctx.token, tenant_id, api_key=ctx.api_key) or {}
            published = None
            effective: dict = {}
            if isinstance(flow_info, dict) and flow_info.get("error"):
                status_code = str(flow_info.get("status_code") or "")
                if status_code == "409":
                    if health_status not in {"NO_PUBLISHED", "MULTIPLE_PUBLISHED"}:
                        st.warning("No se pudo resolver el flow publicado.")
                else:
                    st.error(flow_info)
            else:
                published = flow_info.get("published") if isinstance(flow_info.get("published"), dict) else None
                scopes = flow_info.get("scopes") or []
                if published and flow_system == "v2":
                    badge = pill("PUBLICADO", "success")
                    st.markdown(
                        f"{badge} v{published.get('version')} · `{published.get('flow_id')}` · {published.get('published_at') or '—'}",
                        unsafe_allow_html=True,
                    )
                else:
                    st.info(f"Fallback a base del scope: {scopes[0] if scopes else '—'}")
                effective = flow_info.get("effective_flow") if isinstance(flow_info.get("effective_flow"), dict) else {}
                st.caption(
                    f"start_block: `{effective.get('start_block') or '—'}` · blocks: {len((effective.get('blocks') or {}) if isinstance(effective.get('blocks'), dict) else {})}"
                )
                show_json = st.checkbox("Ver JSON (solo lectura)", value=False, key=f"show-json-{tenant_id}")
                if show_json:
                    st.json(effective or {})
            if debug_mode and isinstance(published, dict):
                st.caption(
                    f"Flow publicado actual: `{published.get('flow_id')}` · v{published.get('version')} · {published.get('published_at') or '—'}"
                )

            multiple_published = any(r.get("status") == "MULTIPLE_PUBLISHED" for r in scope_rows)
            if multiple_published:
                st.error("Hay más de un flow publicado en algún scope. Corrige antes de operar.")

            st.markdown("**Publicar flow**")
            publish_disabled = not write_enabled or multiple_published or not isinstance(effective, dict) or not effective
            publish_confirm = st.checkbox(
                "Confirmo que quiero publicar este flow y despublicar versiones anteriores.",
                value=False,
                key=f"pub-confirm-{tenant_id}",
                disabled=not write_enabled,
            )
            publish_phrase = st.text_input(
                "Escribe PUBLICAR para habilitar",
                value="",
                key=f"pub-text-{tenant_id}",
                disabled=not publish_confirm or not write_enabled,
            )
            can_publish = publish_confirm and publish_phrase.strip().lower() == "publicar"
            publish_block_reason = None
            publish_block_level = "info"
            if multiple_published:
                publish_block_reason = "Bloqueado: hay múltiples flows publicados (backend devolvería 409)."
                publish_block_level = "error"
            elif health_status == "NO_PUBLISHED" and not effective:
                publish_block_reason = "No hay flow publicado. Publica uno para habilitar el chat."
                publish_block_level = "warning"
            elif not can_publish:
                publish_block_reason = "Completa confirmación: marca checkbox + escribe PUBLICAR."
                publish_block_level = "info"
            elif not isinstance(effective, dict) or not effective:
                publish_block_reason = "Selecciona la versión a publicar."
                publish_block_level = "info"
            if publish_disabled and publish_block_reason:
                if publish_block_level == "error":
                    st.error(publish_block_reason)
                elif publish_block_level == "warning":
                    st.warning(publish_block_reason)
                else:
                    st.info(publish_block_reason)
            if st.button(
                "Publicar flow efectivo",
                key=f"publish-flow-{tenant_id}",
                use_container_width=True,
                disabled=publish_disabled or not can_publish,
            ):
                res = publish_flow(ctx.token, tenant_id, effective, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Flow publicado.")
                    st.rerun()

            st.markdown("**Probar resolución backend**")
            if st.button(
                "Probar resolución backend",
                key=f"resolve-flow-{tenant_id}",
                use_container_width=True,
            ):
                res = get_published_flow(ctx.token, tenant_id, api_key=ctx.api_key)
                status = str(res.get("status") or "")
                if status == "OK":
                    flow = res.get("flow") or {}
                    msg = (
                        f"Resolved active flow → tenant={tenant_id} "
                        f"flow={flow.get('flow_id')} version={flow.get('version')} "
                        f"published_at={flow.get('published_at')}"
                    )
                    st.code(msg, language="text")
                elif status == "NO_PUBLISHED":
                    st.warning("No hay flow publicado. El chat devolverá 409.")
                elif status == "MULTIPLE_PUBLISHED":
                    st.error("Hay múltiples flows publicados. Corrige antes de operar.")
                else:
                    st.warning(res)

            if debug_mode:
                st.markdown("**Debug**")
                reset_confirm = st.checkbox(
                    "Confirmo resetear sesiones activas del tenant.",
                    value=False,
                    key=f"reset-confirm-{tenant_id}",
                    disabled=not write_enabled,
                )
                reset_text = st.text_input(
                    "Escribe RESET para confirmar",
                    value="",
                    key=f"reset-text-{tenant_id}",
                    disabled=not reset_confirm or not write_enabled,
                )
                reset_ready = reset_confirm and reset_text.strip().lower() == "reset" and write_enabled
                if st.button(
                    "Reset sesiones",
                    key=f"reset-sessions-{tenant_id}",
                    use_container_width=True,
                    disabled=not reset_ready,
                ):
                    res = reset_sessions(ctx.token, tenant_id, api_key=ctx.api_key)
                    if isinstance(res, dict) and res.get("error"):
                        code = int(res.get("status_code") or 0)
                        if code in {404, 405}:
                            st.info("Reset sesiones: no hay endpoint disponible (backend ya invalida por versión).")
                        else:
                            st.error(res)
                    else:
                        st.success("Sesiones reseteadas.")

            st.caption("Tip: abre el Widget tester con este tenant para ver claramente qué flow se prueba.")
            if st.button("Abrir Widget tester (este tenant)", key=f"open-wt-{tenant_id}", use_container_width=True):
                st.session_state["_widget_tester_tenant_id"] = tenant_id
                st.switch_page("pages/widget_tester.py")
