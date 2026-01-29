from __future__ import annotations

import json
import re
from typing import Any

import streamlit as st

from admin_panel.api_client import (
    create_scope,
    get_catalog,
    import_flow_base,
    publish_flow_by_id,
    create_subflow,
    import_subflow,
    publish_subflow,
    update_subflow,
    simulate_subflow,
    list_tenants,
    tenant_flow_sync,
    tenant_flow_publish_override,
    clone_subflows_to_tenant,
)
from admin_panel.ui import init_page, render_sidebar_nav, require_admin_context, pill


SLUG_RE = re.compile(r"^[a-z0-9_\-]{2,}$")

_WIZ_LEGACY_KEYS = {
    "wiz_step": "wizard_step",
    "wiz_vertical_key": "wizard_vertical_key",
    "wiz_scope_key": "wizard_scope_key",
    "wiz_base_flow_id": "wizard_base_flow_id",
}


def _wiz_get(key: str, default: Any | None = None) -> Any | None:
    if key in st.session_state:
        return st.session_state.get(key, default)
    legacy = _WIZ_LEGACY_KEYS.get(key)
    if legacy:
        return st.session_state.get(legacy, default)
    return default


def _wiz_set(key: str, value: Any) -> None:
    st.session_state[key] = value
    legacy = _WIZ_LEGACY_KEYS.get(key)
    if legacy:
        st.session_state[legacy] = value


def _init_state() -> None:
    for key, default in (
        ("wiz_step", 1),
        ("wiz_vertical_key", ""),
        ("wiz_scope_key", ""),
        ("wiz_base_flow_id", None),
    ):
        if key not in st.session_state:
            legacy = _WIZ_LEGACY_KEYS.get(key)
            if legacy in st.session_state and st.session_state.get(legacy) not in (None, ""):
                st.session_state[key] = st.session_state.get(legacy)
            else:
                st.session_state[key] = default
        legacy = _WIZ_LEGACY_KEYS.get(key)
        if legacy and legacy not in st.session_state:
            st.session_state[legacy] = st.session_state.get(key)
    st.session_state.setdefault("wizard_scope_mode", "existing")
    st.session_state.setdefault("wizard_scope_display", "")
    st.session_state.setdefault("wizard_scope_desc", "")
    st.session_state.setdefault("wizard_base_flow_version", None)
    st.session_state.setdefault("wizard_base_action", "existing")
    st.session_state.setdefault("wizard_sim_text", "")
    st.session_state.setdefault("wizard_sim_tenant", "")
    st.session_state.setdefault("wizard_tenant_selection", [])


def _reset_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("wizard_") or key.startswith("wiz_"):
            st.session_state.pop(key, None)
    _init_state()


def _slug_ok(value: str) -> bool:
    return bool(SLUG_RE.match(value or ""))


def _parse_flow_file(file_bytes: bytes) -> dict[str, Any] | None:
    try:
        data = json.loads(file_bytes.decode("utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("blocks"), dict) or not data.get("blocks"):
        return None
    if not data.get("start_block"):
        return None
    return data


def _flows_for_scope(catalog: dict, vertical_key: str, scope_key: str) -> list[dict]:
    for v in catalog.get("verticals") or []:
        if v.get("vertical_key") != vertical_key:
            continue
        for s in v.get("scopes") or []:
            if s.get("scope_key") == scope_key:
                return s.get("flows") or []
    return []


def _flow_entries(
    flows: list[dict], *, flow_kind: str, parent_flow_id: str | None = None
) -> list[dict]:
    out = []
    for f in flows:
        if str(f.get("flow_kind") or "").lower() != flow_kind:
            continue
        if parent_flow_id and str(f.get("parent_flow_id") or "") != str(parent_flow_id):
            continue
        out.append(f)
    return out


def _catalog_verticals(catalog: dict) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(catalog, dict):
        return out
    for item in catalog.get("verticals") or []:
        if not isinstance(item, dict):
            continue
        vkey = item.get("vertical_key") or item.get("key")
        if not vkey:
            continue
        out.append(
            {
                "vertical_key": str(vkey),
                "label": item.get("name") or item.get("label") or str(vkey),
                "raw": item,
            }
        )
    return out


def _catalog_scopes(catalog: dict) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(catalog, dict):
        return out
    for item in catalog.get("scopes") or []:
        if not isinstance(item, dict):
            continue
        vkey = item.get("vertical_key")
        skey = item.get("scope_key")
        if vkey and skey:
            out.append(item)
    for v in catalog.get("verticals") or []:
        if not isinstance(v, dict):
            continue
        vkey = v.get("vertical_key")
        for s in v.get("scopes") or []:
            if not isinstance(s, dict):
                continue
            skey = s.get("scope_key")
            if not vkey or not skey:
                continue
            entry = dict(s)
            entry.setdefault("vertical_key", vkey)
            out.append(entry)
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for scope in out:
        key = (str(scope.get("vertical_key")), str(scope.get("scope_key")))
        unique[key] = scope
    return list(unique.values())


init_page(title="Wizard completo", icon="⚡")
ctx = require_admin_context()
render_sidebar_nav()

if not ctx.is_super_admin:
    st.warning("Esta herramienta está disponible solo para SUPER_ADMIN.")
    st.stop()

_init_state()

step = int(_wiz_get("wiz_step") or 1)
step = min(max(step, 1), 7)

st.title("⚡ Wizard completo")
st.caption("Crear flow base + subflows + routing + publicar + asignar tenants.")

progress = (step - 1) / 6
st.progress(progress)
st.markdown(f"**Paso {step}/7**")

catalog = get_catalog(
    ctx.token,
    include_empty_scopes=True,
    include_drafts=True,
    include_templates=True,
    api_key=ctx.api_key,
)
vertical_options = _catalog_verticals(catalog if isinstance(catalog, dict) else {})
vertical_options = sorted(vertical_options, key=lambda v: str(v.get("label") or ""))
scopes_all = _catalog_scopes(catalog if isinstance(catalog, dict) else {})
scopes_for_vertical = [
    s for s in scopes_all if str(s.get("vertical_key") or "") == str(_wiz_get("wiz_vertical_key") or "")
]

if st.session_state.get("debug"):
    st.write("DEBUG wiz_step:", _wiz_get("wiz_step"))
    st.write("DEBUG wiz_vertical_key:", repr(_wiz_get("wiz_vertical_key")))
    st.write("DEBUG catalog verticals count:", len(vertical_options))
    st.write("DEBUG scopes found:", len(scopes_for_vertical))

if step == 1:
    st.subheader("1) Elegir vertical")
    selected_vertical: dict[str, Any] | None = None
    if vertical_options:
        current_vkey = str(_wiz_get("wiz_vertical_key") or "")
        index = 0
        if current_vkey:
            for i, opt in enumerate(vertical_options):
                if str(opt.get("vertical_key")) == current_vkey:
                    index = i
                    break
        selected_vertical = st.selectbox(
            "Vertical",
            options=vertical_options,
            index=index,
            format_func=lambda o: o.get("label") or o.get("vertical_key") or "",
            key="wiz_vertical_select",
        )
        if selected_vertical and selected_vertical.get("vertical_key"):
            if str(selected_vertical.get("vertical_key")) != current_vkey:
                _wiz_set("wiz_vertical_key", str(selected_vertical.get("vertical_key")))
    else:
        st.info("No hay verticales en catálogo. Crea un scope desde Scopes o configura verticals.")
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        can_continue = bool(selected_vertical and selected_vertical.get("vertical_key"))
        if st.button("Continuar", use_container_width=True, disabled=not can_continue):
            _wiz_set("wiz_vertical_key", str(selected_vertical.get("vertical_key")))
            _wiz_set("wiz_step", 2)
            st.rerun()
    with c2:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 2:
    st.subheader("2) Scope")
    vkey = str(_wiz_get("wiz_vertical_key") or "")
    if not vkey:
        st.warning("Selecciona un vertical primero.")
        _wiz_set("wiz_step", 1)
        st.rerun()
    st.caption(f"Vertical: `{vkey}`")

    mode = st.radio(
        "",
        options=["existing", "new"],
        format_func=lambda v: "Usar existente" if v == "existing" else "Crear nuevo",
        index=0 if st.session_state.get("wizard_scope_mode") != "new" else 1,
        key="wizard_scope_mode",
        horizontal=True,
    )

    scope_key = ""
    selected_scope: dict[str, Any] | None = None
    if mode == "existing":
        scopes_for_vertical = [
            s for s in scopes_all if str(s.get("vertical_key") or "") == vkey
        ]
        scopes_for_vertical = sorted(scopes_for_vertical, key=lambda s: str(s.get("scope_key") or ""))
        if scopes_for_vertical:
            scope_options = [
                {
                    "scope_key": s.get("scope_key"),
                    "label": s.get("display_name") or s.get("name") or s.get("scope_key"),
                }
                for s in scopes_for_vertical
                if s.get("scope_key")
            ]
            current_scope = str(_wiz_get("wiz_scope_key") or "")
            index = 0
            if current_scope:
                for i, opt in enumerate(scope_options):
                    if str(opt.get("scope_key")) == current_scope:
                        index = i
                        break
            selected_scope = st.selectbox(
                "Scope",
                options=scope_options,
                index=index,
                format_func=lambda o: o.get("label") or o.get("scope_key") or "",
                key="wiz_scope_select",
            )
            if selected_scope and selected_scope.get("scope_key"):
                if str(selected_scope.get("scope_key")) != current_scope:
                    _wiz_set("wiz_scope_key", str(selected_scope.get("scope_key")))
            scope_key = str(selected_scope.get("scope_key") or "") if selected_scope else ""
        else:
            st.info("No hay scopes para este vertical. Puedes crear uno nuevo.")
    else:
        scope_key_input = st.text_input("Scope key (slug)", key="wiz_scope_key_input")
        st.text_input("Nombre visible", key="wizard_scope_display")
        st.text_area("Descripción (opcional)", key="wizard_scope_desc", height=80)
        scope_key = scope_key_input or ""
        if scope_key != str(_wiz_get("wiz_scope_key") or ""):
            _wiz_set("wiz_scope_key", scope_key)

    can_continue = bool(scope_key) and bool(vkey)
    if mode == "new":
        display = st.session_state.get("wizard_scope_display") or ""
        if scope_key and not _slug_ok(scope_key):
            st.warning("Scope key inválido. Usa solo [a-z0-9_-], mínimo 2 caracteres.")
        can_continue = _slug_ok(scope_key) and bool(display)
        if scope_key and _slug_ok(scope_key) and not display:
            st.warning("Completa el nombre visible para continuar.")
    elif not scope_key:
        st.warning("Selecciona un scope existente o cambia a “Crear nuevo”.")

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Continuar", use_container_width=True, disabled=not can_continue):
            if mode == "new":
                res = create_scope(
                    ctx.token,
                    vertical_key=vkey,
                    scope_key=scope_key.strip(),
                    display_name=st.session_state.get("wizard_scope_display") or "",
                    description=st.session_state.get("wizard_scope_desc") or None,
                    api_key=ctx.api_key,
                )
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                    st.stop()
            _wiz_set("wiz_scope_key", scope_key)
            _wiz_set("wiz_step", 3)
            st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            _wiz_set("wiz_step", 1)
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 3:
    st.subheader("3) Flow base")
    vkey = str(_wiz_get("wiz_vertical_key") or "")
    skey = str(_wiz_get("wiz_scope_key") or "")
    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}`")

    flows = _flows_for_scope(catalog, vkey, skey)
    base_flows = _flow_entries(flows, flow_kind="base")
    published_base = [f for f in base_flows if f.get("published")]
    action = st.radio(
        "",
        options=["existing", "import"],
        format_func=lambda v: "Usar base publicado" if v == "existing" else "Importar JSON como nueva version",
        index=0 if st.session_state.get("wizard_base_action") == "existing" else 1,
        key="wizard_base_action",
        horizontal=True,
    )

    selected_base = None
    if action == "existing":
        if not published_base:
            st.warning("No hay base publicado. Importa un JSON.")
        else:
            options = [f"{f.get('name')} · {f.get('flow_id')}" for f in published_base]
            idx = st.selectbox("Base publicado", options=options)
            selected_base = published_base[options.index(idx)]
    else:
        upload = st.file_uploader("Archivo JSON del flow base", type=["json"], key="wizard_flow_file")
        parsed = None
        if upload:
            parsed = _parse_flow_file(upload.getvalue())
            if not parsed:
                st.error("JSON inválido o faltan campos (start_block/blocks).")
            else:
                st.success("JSON válido.")
                st.write({"start_block": parsed.get("start_block"), "blocks": len(parsed.get("blocks") or {})})

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        can_continue = False
        if action == "existing":
            can_continue = selected_base is not None
        else:
            can_continue = upload is not None and parsed is not None
        if st.button("Continuar", use_container_width=True, disabled=not can_continue):
            if action == "existing" and selected_base is not None:
                _wiz_set("wiz_base_flow_id", selected_base.get("flow_id"))
                st.session_state["wizard_base_flow_version"] = selected_base.get("version")
            else:
                res = import_flow_base(
                    ctx.token,
                    file_name=upload.name,
                    file_bytes=upload.getvalue(),
                    vertical_key=vkey,
                    scope_key=skey,
                    owner_type="GLOBAL",
                    owner_id=None,
                    api_key=ctx.api_key,
                )
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                    st.stop()
                _wiz_set("wiz_base_flow_id", res.get("flow_id"))
                st.session_state["wizard_base_flow_version"] = res.get("version")
            _wiz_set("wiz_step", 4)
            st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            _wiz_set("wiz_step", 2)
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 4:
    st.subheader("4) Subflows")
    vkey = str(_wiz_get("wiz_vertical_key") or "")
    skey = str(_wiz_get("wiz_scope_key") or "")
    base_flow_id = _wiz_get("wiz_base_flow_id")
    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}` · Base: `{base_flow_id}`")

    flows = _flows_for_scope(catalog, vkey, skey)
    subflows = _flow_entries(flows, flow_kind="subflow", parent_flow_id=str(base_flow_id))
    if subflows:
        st.markdown("**Subflows existentes**")
        for f in subflows:
            status = "PUBLISHED" if f.get("published") else "DRAFT"
            st.write(
                {
                    "subflow_key": f.get("subflow_key"),
                    "flow_id": f.get("flow_id"),
                    "status": status,
                    "owner_type": f.get("owner_type"),
                    "enabled": f.get("enabled", True),
                    "priority": f.get("trigger_priority"),
                    "threshold": f.get("trigger_threshold"),
                }
            )
            enabled_key = f"enabled-{f.get('flow_id')}"
            enabled_value = st.toggle(
                "Activo",
                value=bool(f.get("enabled", True)),
                key=enabled_key,
            )
            if enabled_value != bool(f.get("enabled", True)):
                res = update_subflow(
                    ctx.token,
                    str(f.get("flow_id")),
                    {"enabled": bool(enabled_value)},
                    api_key=ctx.api_key,
                )
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Estado actualizado.")
                    st.rerun()
    else:
        st.info("No hay subflows aún para este base.")

    with st.expander("Añadir subflow", expanded=False):
        tab_quick, tab_import = st.tabs(["Rapido", "Importar JSON"])
        with tab_quick:
            display_name = st.text_input("Nombre", value="")
            subflow_key = st.text_input("subflow_key (slug)", value="")
            content_text = st.text_area("Texto base", value="", height=120)
            keywords = st.text_input("Keywords (coma)", value="")
            priority = st.slider("Prioridad", 1, 10, 5)
            threshold = st.slider("Umbral", 1, 5, 1)
            if st.button("Crear subflow", use_container_width=True):
                payload = {
                    "vertical_key": vkey,
                    "scope_key": skey,
                    "parent_flow_id": base_flow_id,
                    "subflow_key": subflow_key.strip() or None,
                    "display_name": display_name.strip() or subflow_key.strip() or "Subflow",
                    "content_text": content_text.strip() or "",
                    "trigger_keywords": [k.strip() for k in keywords.split(",") if k.strip()],
                    "trigger_priority": priority,
                    "trigger_threshold": threshold,
                    "owner_type": "GLOBAL",
                    "owner_id": None,
                }
                res = create_subflow(ctx.token, payload, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    st.error(res)
                else:
                    st.success("Subflow creado.")
                    st.rerun()
        with tab_import:
            subflow_file = st.file_uploader("Archivo JSON subflow", type=["json"], key="wizard_subflow_file")
            subflow_key_file = st.text_input("subflow_key", value="")
            keywords_file = st.text_input("Keywords (coma)", value="")
            priority_file = st.slider("Prioridad", 1, 10, 5, key="sf-prio")
            threshold_file = st.slider("Umbral", 1, 5, 1, key="sf-thresh")
            if st.button("Importar subflow", use_container_width=True, disabled=subflow_file is None):
                parsed = _parse_flow_file(subflow_file.getvalue()) if subflow_file else None
                if not parsed:
                    st.error("JSON inválido o faltan campos (start_block/blocks).")
                else:
                    res = import_subflow(
                        ctx.token,
                        file_name=subflow_file.name,
                        file_bytes=subflow_file.getvalue(),
                        vertical_key=vkey,
                        scope_key=skey,
                        parent_flow_id=str(base_flow_id),
                        subflow_key=subflow_key_file.strip(),
                        trigger_keywords=keywords_file.strip() or None,
                        trigger_priority=priority_file,
                        trigger_threshold=threshold_file,
                        owner_type="GLOBAL",
                        owner_id=None,
                        api_key=ctx.api_key,
                    )
                    if isinstance(res, dict) and res.get("error"):
                        st.error(res)
                    else:
                        st.success("Subflow importado.")
                        st.rerun()

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Continuar", use_container_width=True, disabled=not bool(base_flow_id)):
            _wiz_set("wiz_step", 5)
            st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            _wiz_set("wiz_step", 3)
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 5:
    st.subheader("5) Routing")
    vkey = str(_wiz_get("wiz_vertical_key") or "")
    skey = str(_wiz_get("wiz_scope_key") or "")
    base_flow_id = _wiz_get("wiz_base_flow_id")
    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}` · Base: `{base_flow_id}`")

    flows = _flows_for_scope(catalog, vkey, skey)
    subflows = _flow_entries(flows, flow_kind="subflow", parent_flow_id=str(base_flow_id))
    if not subflows:
        st.info("No hay subflows para configurar.")
    else:
        st.markdown("**Configurar routing**")
        for sf in subflows:
            with st.expander(
                f"{sf.get('subflow_key')} ({'PUBLISHED' if sf.get('published') else 'DRAFT'}) · {sf.get('owner_type')}",
                expanded=False,
            ):
                kw_default = ", ".join(sf.get("trigger_keywords") or []) if isinstance(sf.get("trigger_keywords"), list) else ""
                kw = st.text_input("Keywords", value=kw_default, key=f"kw-{sf.get('flow_id')}")
                pr = st.slider("Prioridad", 1, 10, int(sf.get("trigger_priority") or 5), key=f"pr-{sf.get('flow_id')}")
                th = st.slider("Umbral", 1, 5, int(sf.get("trigger_threshold") or 1), key=f"th-{sf.get('flow_id')}")
                enabled_state = st.checkbox(
                    "Activo",
                    value=bool(sf.get("enabled", True)),
                    key=f"en-{sf.get('flow_id')}",
                )
                if st.button("Guardar", key=f"save-{sf.get('flow_id')}"):
                    payload = {
                        "trigger_keywords": [k.strip() for k in kw.split(",") if k.strip()],
                        "trigger_priority": pr,
                        "trigger_threshold": th,
                        "enabled": bool(enabled_state),
                    }
                    res = update_subflow(ctx.token, str(sf.get("flow_id")), payload, api_key=ctx.api_key)
                    if isinstance(res, dict) and res.get("error"):
                        st.error(res)
                    else:
                        st.success("Routing actualizado.")
                        st.rerun()

    st.markdown("**Probar routing**")
    tenants_payload = list_tenants(ctx.token, api_key=ctx.api_key) or []
    tenants = tenants_payload if isinstance(tenants_payload, list) else tenants_payload.get("items") or []
    tenant_options = [t for t in tenants if t.get("vertical_key") == vkey]
    tenant_map = {t.get("name") or t.get("id"): t for t in tenant_options if t.get("id")}
    names = list(tenant_map.keys())
    tenant_choice = None
    if not names:
        st.info("No hay tenants para este vertical.")
    else:
        tenant_choice = st.selectbox("Tenant", options=names, index=0)
    text = st.text_input("Texto de usuario", value=st.session_state.get("wizard_sim_text") or "")
    if st.button("Simular routing", use_container_width=True, disabled=not (tenant_choice and text)):
        tenant_id = tenant_map.get(tenant_choice, {}).get("id") if tenant_choice else ""
        res = simulate_subflow(
            ctx.token,
            tenant_id=str(tenant_id),
            base_flow_id=str(base_flow_id),
            text=text,
            api_key=ctx.api_key,
        )
        if isinstance(res, dict) and res.get("error"):
            st.error(res)
        else:
            st.success("Simulacion OK")
            st.json(res)

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Continuar", use_container_width=True):
            _wiz_set("wiz_step", 6)
            st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            _wiz_set("wiz_step", 4)
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 6:
    st.subheader("6) Publicar en lote")
    vkey = str(_wiz_get("wiz_vertical_key") or "")
    skey = str(_wiz_get("wiz_scope_key") or "")
    base_flow_id = _wiz_get("wiz_base_flow_id")
    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}` · Base: `{base_flow_id}`")

    flows = _flows_for_scope(catalog, vkey, skey)
    base_entries = [f for f in _flow_entries(flows, flow_kind="base") if str(f.get("flow_id")) == str(base_flow_id)]
    base_published = bool(base_entries and base_entries[0].get("published"))

    subflows = _flow_entries(flows, flow_kind="subflow", parent_flow_id=str(base_flow_id))
    publish_subflow_ids = []
    for sf in subflows:
        label = f"{sf.get('subflow_key')} ({'PUBLISHED' if sf.get('published') else 'DRAFT'})"
        if st.checkbox(label, value=bool(sf.get("published")), key=f"pub-sf-{sf.get('flow_id')}"):
            publish_subflow_ids.append(sf.get("flow_id"))

    confirm = st.checkbox("Confirmo publicacion masiva", value=False)
    confirm_text = st.text_input("Escribe PUBLICAR para habilitar", value="")
    can_publish = confirm and confirm_text.strip().lower() == "publicar"

    if st.button("Publicar ahora", use_container_width=True, disabled=not can_publish):
        if not base_published and base_flow_id:
            res = publish_flow_by_id(ctx.token, str(base_flow_id), api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                st.error(res)
                st.stop()
        for flow_id in publish_subflow_ids:
            res = publish_subflow(ctx.token, str(flow_id), api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                st.error(res)
                st.stop()
        st.success("Publicacion completada.")
        _wiz_set("wiz_step", 7)
        st.rerun()

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Continuar", use_container_width=True):
            _wiz_set("wiz_step", 7)
            st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            _wiz_set("wiz_step", 5)
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

else:
    st.subheader("7) Asignar a tenants")
    vkey = str(_wiz_get("wiz_vertical_key") or "")
    skey = str(_wiz_get("wiz_scope_key") or "")
    base_flow_id = _wiz_get("wiz_base_flow_id")
    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}` · Base: `{base_flow_id}`")

    tenants_payload = list_tenants(ctx.token, api_key=ctx.api_key) or []
    tenants = tenants_payload if isinstance(tenants_payload, list) else tenants_payload.get("items") or []
    tenant_options = [t for t in tenants if t.get("vertical_key") == vkey]
    tenant_map = {t.get("name") or t.get("id"): t for t in tenant_options if t.get("id")}
    names = list(tenant_map.keys())
    selected_names = st.multiselect("Tenants", options=names, default=st.session_state.get("wizard_tenant_selection") or [])
    st.session_state["wizard_tenant_selection"] = selected_names

    if st.button("Sync now", use_container_width=True, disabled=not selected_names):
        results = []
        for name in selected_names:
            t = tenant_map.get(name) or {}
            res = tenant_flow_sync(
                ctx.token,
                t.get("id"),
                vertical_key=vkey,
                scope_key=skey,
                flow_kind="base",
                api_key=ctx.api_key,
            )
            results.append({"tenant": name, "result": res})
        st.json(results)

    if st.button("Publish override", use_container_width=True, disabled=not selected_names):
        results = []
        for name in selected_names:
            t = tenant_map.get(name) or {}
            res = tenant_flow_publish_override(
                ctx.token,
                t.get("id"),
                vertical_key=vkey,
                scope_key=skey,
                flow_kind="base",
                published=True,
                api_key=ctx.api_key,
            )
            results.append({"tenant": name, "result": res})
        st.json(results)

    if st.button("Crear override de subflows", use_container_width=True, disabled=not selected_names):
        results = []
        for name in selected_names:
            t = tenant_map.get(name) or {}
            res = clone_subflows_to_tenant(
                ctx.token,
                {"tenant_id": t.get("id"), "base_flow_id": str(base_flow_id)},
                api_key=ctx.api_key,
            )
            results.append({"tenant": name, "result": res})
        st.json(results)

    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        if st.button("Crear otro", use_container_width=True):
            _reset_state()
            st.rerun()
    with c2:
        st.page_link("pages/02_🏢_Tenants.py", label="Abrir Tenants", icon="🏢")
