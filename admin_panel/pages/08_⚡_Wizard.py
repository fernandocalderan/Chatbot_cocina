from __future__ import annotations

import json
import re
from typing import Any

import streamlit as st

from admin_panel.api_client import create_scope, get_catalog, import_flow_base, publish_flow_by_id
from admin_panel.ui import init_page, render_sidebar_nav, require_admin_context, pill


SLUG_RE = re.compile(r"^[a-z0-9_]{3,}$")


def _init_state() -> None:
    st.session_state.setdefault("wizard_step", 1)
    st.session_state.setdefault("wizard_vertical_mode", "existing")
    st.session_state.setdefault("wizard_vertical_key", "")
    st.session_state.setdefault("wizard_new_vertical_key", "")
    st.session_state.setdefault("wizard_scope_key", "")
    st.session_state.setdefault("wizard_scope_display", "")
    st.session_state.setdefault("wizard_scope_desc", "")
    st.session_state.setdefault("wizard_flow_file", None)
    st.session_state.setdefault("wizard_flow_info", {})
    st.session_state.setdefault("wizard_flow_id", None)
    st.session_state.setdefault("wizard_flow_version", None)


def _reset_state() -> None:
    keys = [
        "wizard_step",
        "wizard_vertical_mode",
        "wizard_vertical_key",
        "wizard_new_vertical_key",
        "wizard_scope_key",
        "wizard_scope_display",
        "wizard_scope_desc",
        "wizard_flow_file",
        "wizard_flow_info",
        "wizard_flow_id",
        "wizard_flow_version",
    ]
    for k in keys:
        st.session_state.pop(k, None)
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


init_page(title="Wizard 60s", icon="⚡")
ctx = require_admin_context()
render_sidebar_nav()

if not ctx.is_super_admin:
    st.warning("Esta herramienta está disponible solo para SUPER_ADMIN.")
    st.stop()

_init_state()

step = int(st.session_state.get("wizard_step") or 1)
step = min(max(step, 1), 5)

st.title("⚡ Wizard (60 segundos)")
st.caption("Crea una plantilla base en minutos: Vertical → Área (Scope) → Flow base → Publicar.")

progress = (step - 1) / 4
st.progress(progress)
st.markdown(f"**Paso {step}/5**")

catalog = get_catalog(
    ctx.token,
    include_empty_scopes=True,
    include_drafts=True,
    include_templates=True,
    api_key=ctx.api_key,
)
verticals = []
if isinstance(catalog, dict) and catalog.get("verticals"):
    verticals = [v.get("vertical_key") for v in catalog.get("verticals") if v.get("vertical_key")]
verticals = sorted({v for v in verticals if v})

if step == 1:
    st.subheader("1) Elige Vertical")
    mode = st.radio(
        "",
        options=["existing", "new"],
        format_func=lambda v: "Usar vertical existente" if v == "existing" else "Crear nueva vertical",
        index=0 if st.session_state.get("wizard_vertical_mode") != "new" else 1,
        horizontal=True,
        key="wizard_vertical_mode",
    )
    if mode == "existing":
        if verticals:
            selected = st.selectbox("Vertical", options=verticals, key="wizard_vertical_key")
        else:
            st.info("No hay verticales en catálogo. Crea una nueva vertical.")
            st.session_state["wizard_vertical_mode"] = "new"
    if st.session_state.get("wizard_vertical_mode") == "new":
        st.text_input(
            "Nueva vertical_key (slug)",
            value=st.session_state.get("wizard_new_vertical_key") or "",
            key="wizard_new_vertical_key",
            help="Solo minúsculas, números y guion bajo. Ej: clinics_private",
        )

    ready = False
    if st.session_state.get("wizard_vertical_mode") == "existing":
        ready = bool(st.session_state.get("wizard_vertical_key"))
    else:
        new_key = st.session_state.get("wizard_new_vertical_key") or ""
        ready = _slug_ok(new_key)
        if new_key and not _slug_ok(new_key):
            st.warning("Formato inválido. Usa solo [a-z0-9_], mínimo 3 caracteres.")

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        if st.button("Continuar", use_container_width=True, disabled=not ready):
            if st.session_state.get("wizard_vertical_mode") == "new":
                st.session_state["wizard_vertical_key"] = st.session_state.get("wizard_new_vertical_key", "")
            st.session_state["wizard_step"] = 2
            st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 2:
    st.subheader("2) Crear área (Scope)")
    vkey = st.session_state.get("wizard_vertical_key") or ""
    st.caption(f"Vertical: `{vkey}`")

    st.text_input("Scope key (slug)", key="wizard_scope_key")
    st.text_input("Nombre visible", key="wizard_scope_display")
    st.text_area("Descripción (opcional)", key="wizard_scope_desc", height=80)

    scope_key = st.session_state.get("wizard_scope_key") or ""
    display = st.session_state.get("wizard_scope_display") or ""

    exists = False
    for v in catalog.get("verticals") or []:
        if v.get("vertical_key") == vkey:
            exists = any(s.get("scope_key") == scope_key for s in (v.get("scopes") or []))
            break

    if scope_key and not _slug_ok(scope_key):
        st.warning("Scope key inválido. Usa solo [a-z0-9_], mínimo 3 caracteres.")
    if exists:
        st.error("Ese scope ya existe. Elige otro key.")

    can_create = _slug_ok(scope_key) and bool(display) and not exists

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Crear área (Scope)", use_container_width=True, disabled=not can_create):
            res = create_scope(
                ctx.token,
                vertical_key=vkey,
                scope_key=scope_key,
                display_name=display,
                description=st.session_state.get("wizard_scope_desc") or None,
                api_key=ctx.api_key,
            )
            if isinstance(res, dict) and res.get("error"):
                st.error(res)
            else:
                st.success("Scope creado.")
                st.session_state["wizard_step"] = 3
                st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            st.session_state["wizard_step"] = 1
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 3:
    st.subheader("3) Subir Flow Base")
    vkey = st.session_state.get("wizard_vertical_key") or ""
    skey = st.session_state.get("wizard_scope_key") or ""
    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}`")

    upload = st.file_uploader("Archivo JSON del flow base", type=["json"], key="wizard_flow_file")
    parsed = None
    if upload:
        parsed = _parse_flow_file(upload.getvalue())
        if not parsed:
            st.error("JSON inválido o faltan campos (start_block/blocks).")
        else:
            st.success("JSON válido.")
            st.write(
                {
                    "start_block": parsed.get("start_block"),
                    "blocks": len(parsed.get("blocks") or {}),
                }
            )

    can_import = bool(upload) and parsed is not None

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Importar como borrador", use_container_width=True, disabled=not can_import):
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
            else:
                st.session_state["wizard_flow_id"] = res.get("flow_id")
                st.session_state["wizard_flow_version"] = res.get("version")
                st.success("Flow importado como borrador.")
                st.session_state["wizard_step"] = 4
                st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            st.session_state["wizard_step"] = 2
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

elif step == 4:
    st.subheader("4) Publicar")
    vkey = st.session_state.get("wizard_vertical_key") or ""
    skey = st.session_state.get("wizard_scope_key") or ""
    flow_id = st.session_state.get("wizard_flow_id")
    version = st.session_state.get("wizard_flow_version")

    st.caption(f"Vertical: `{vkey}` · Scope: `{skey}`")
    st.info("Estás a punto de publicar este flow base. Esto lo deja operativo.")
    if st.session_state.get("debug"):
        st.caption(f"flow_id: `{flow_id}` · version: {version}")

    confirm = st.checkbox("Entiendo que esto lo pone en producción", value=False)
    confirm_text = st.text_input("Escribe PUBLICAR para habilitar", value="")
    can_publish = bool(flow_id) and confirm and confirm_text.strip().lower() == "publicar"

    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        if st.button("Publicar ahora", use_container_width=True, disabled=not can_publish):
            res = publish_flow_by_id(ctx.token, str(flow_id), api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                st.error(res)
            else:
                st.success("Flow publicado.")
                st.session_state["wizard_step"] = 5
                st.rerun()
    with c2:
        if st.button("Volver", use_container_width=True):
            st.session_state["wizard_step"] = 3
            st.rerun()
    with c3:
        if st.button("Cancelar", use_container_width=True):
            _reset_state()
            st.rerun()

else:
    st.subheader("5) Listo")
    vkey = st.session_state.get("wizard_vertical_key") or ""
    skey = st.session_state.get("wizard_scope_key") or ""

    refreshed = get_catalog(
        ctx.token,
        include_empty_scopes=True,
        include_drafts=True,
        include_templates=True,
        api_key=ctx.api_key,
    )
    status = "—"
    for v in refreshed.get("verticals") or []:
        if v.get("vertical_key") != vkey:
            continue
        for s in v.get("scopes") or []:
            if s.get("scope_key") == skey:
                status = s.get("status") or "—"
                break

    tone = "success" if status == "PUBLISHED_OK" else "warning"
    badge = pill(status, tone)
    st.markdown(f"Estado final: {badge}", unsafe_allow_html=True)

    st.success("Listo. Tu scope ya está operativo con flow publicado.")

    c1, c2, c3 = st.columns([0.34, 0.33, 0.33])
    with c1:
        st.page_link("pages/06_🧭_Scopes.py", label="Abrir Scopes", icon="🧭")
    with c2:
        st.page_link("pages/02_🏢_Tenants.py", label="Abrir Tenants", icon="🏢")
    with c3:
        if st.button("Crear otro", use_container_width=True):
            _reset_state()
            st.rerun()
