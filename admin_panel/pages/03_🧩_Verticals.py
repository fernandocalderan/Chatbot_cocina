import sys
from pathlib import Path

import streamlit as st
import json
import re
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_panel.api_client import (
    create_vertical_admin,
    get_vertical,
    list_vertical_files_admin,
    preview_vertical_flow_generator,
    read_vertical_file_admin,
    delete_vertical_file_admin,
    update_vertical_file_admin,
)
from admin_panel.ui import can_write, ensure_vertical_catalog, init_page, render_impersonation_banner, render_sidebar_nav, require_admin_context

init_page(title="SuperAdmin — Verticals", icon="🧩")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

st.title("Verticals")
st.caption(
    "Catálogo de verticales y scopes (sub-verticales). "
    "Modelo simplificado v2: cada scope tiene 1 prompt + 1 flow base (estructura)."
)

write_enabled = can_write(ctx) and not st.session_state.get("impersonation_token")
if not write_enabled:
    st.info("Modo solo lectura: edición/creación de verticales está desactivada.")


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")

_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
_SUBFLOW_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,30}$")


def _is_flow_filename(filename: str) -> bool:
    return (
        filename == "flow_base.json"
        or filename.startswith("flow_base_scope_")
        or filename.startswith("flow_scope_")
        or filename.startswith("subflow_scope_")
    )


def _normalize_blocks_list_to_dict(blocks_list: list[Any]) -> dict[str, Any]:
    blocks: dict[str, Any] = {}
    idx = 1
    for item in blocks_list:
        if not isinstance(item, dict):
            continue
        bid = item.get("id") or item.get("block_id") or item.get("name")
        bid = str(bid or "").strip()
        if not bid:
            bid = f"block_{idx}"
            idx += 1
        block = dict(item)
        block["id"] = block.get("id") or bid
        blocks[bid] = block
    return blocks


def _slugify_subflow_key(raw: str) -> str:
    s = str(raw or "").strip().lower()
    s = re.sub(r"[^a-z0-9_-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_-")
    if not s:
        return "general"
    if not _SUBFLOW_KEY_RE.match(s):
        return "general"
    return s


def _option_id(opt: object) -> str | None:
    if isinstance(opt, dict):
        val = opt.get("id") or opt.get("value")
        return str(val) if val is not None else None
    if opt is None:
        return None
    return str(opt)


def _routes_filename(scope_key: str, save_to: str) -> str:
    scope_key = str(scope_key or "").strip().lower()
    save_to = str(save_to or "").strip().lower()
    if not scope_key or not _KEY_RE.match(scope_key):
        raise ValueError("invalid_scope_key")
    if not save_to or not _KEY_RE.match(save_to):
        raise ValueError("invalid_save_to")
    return f"router_routes_scope_{scope_key}__{save_to}.json"


def _subflow_filename(scope_key: str, save_to: str, subflow_key: str) -> str:
    scope_key = str(scope_key or "").strip().lower()
    save_to = str(save_to or "").strip().lower()
    subflow_key = _slugify_subflow_key(subflow_key)
    if not scope_key or not _KEY_RE.match(scope_key):
        raise ValueError("invalid_scope_key")
    if not save_to or not _KEY_RE.match(save_to):
        raise ValueError("invalid_save_to")
    if not subflow_key or not _KEY_RE.match(subflow_key):
        raise ValueError("invalid_subflow_key")
    return f"subflow_scope_{scope_key}__{save_to}__{subflow_key}.json"


def _subflow_flow_id(*, vertical_key: str, scope_key: str, save_to: str, subflow_key: str) -> str:
    v = str(vertical_key or "").strip().lower()
    s = str(scope_key or "").strip().lower()
    a = str(save_to or "").strip().lower()
    k = _slugify_subflow_key(subflow_key)
    return f"flow_{v}__{s}__{a}__{k}__v1"


def _subflow_skeleton(
    *,
    vertical_key: str,
    scope_key: str,
    save_to: str,
    subflow_key: str,
    label: str | None,
    template_flow: dict[str, Any] | None,
) -> dict[str, Any]:
    tpl = template_flow if isinstance(template_flow, dict) else {}
    languages = tpl.get("languages") if isinstance(tpl.get("languages"), list) else ["es"]
    languages = [str(x) for x in languages if x] or ["es"]
    plan = str(tpl.get("plan") or "base")
    cfg = tpl.get("config") if isinstance(tpl.get("config"), dict) else {}
    cfg = dict(cfg)
    cfg["subflow"] = {
        "vertical_key": str(vertical_key),
        "scope": str(scope_key),
        "router_save_to": str(save_to),
        "key": _slugify_subflow_key(subflow_key),
        "label": (label or "").strip() or None,
    }
    version = _subflow_flow_id(
        vertical_key=vertical_key,
        scope_key=scope_key,
        save_to=save_to,
        subflow_key=subflow_key,
    )
    return {
        "version": version,
        "plan": plan,
        "languages": languages,
        "start_block": "intro",
        "config": cfg,
        "blocks": {
            "intro": {
                "id": "intro",
                "type": "message",
                "text": f"Sub-flow `{label or subflow_key}` (pendiente de configurar).",
                "next": "end",
            },
            "end": {"id": "end", "type": "end"},
        },
    }


def _scaffold_router_subflows(
    flow: dict[str, Any],
    *,
    router_block_id: str,
    save_to: str,
    end_block_id: str = "end",
) -> dict[str, Any]:
    blocks = flow.get("blocks")
    if not isinstance(blocks, dict) or not blocks:
        raise ValueError("missing_blocks")
    router = blocks.get(router_block_id)
    if not isinstance(router, dict):
        raise ValueError("router_block_not_found")
    if (router.get("type") or "").strip().lower() not in {"buttons", "options"}:
        raise ValueError("router_block_not_buttons")
    options = router.get("options") or []
    if not isinstance(options, list) or not options:
        raise ValueError("router_missing_options")

    # Ensure end block exists
    if end_block_id not in blocks:
        blocks[end_block_id] = {"id": end_block_id, "type": "end"}

    # Ensure save_to exists for analytics/vars
    router["save_to"] = str(save_to or "").strip() or "intent"

    routes: dict[str, str] = {}
    for opt in options:
        oid = _option_id(opt)
        if not oid:
            continue
        key = _slugify_subflow_key(oid)
        routes[str(oid)] = key

    if not routes:
        raise ValueError("router_no_valid_options")

    # Router v1-safe: termina aquí (no decide dentro del JSON).
    router["next"] = end_block_id

    # Update config.router metadata (best-effort)
    cfg = flow.get("config") if isinstance(flow.get("config"), dict) else {}
    cfg_router = cfg.get("router") if isinstance(cfg.get("router"), dict) else {}
    cfg_router["block_id"] = router_block_id
    cfg_router["save_to"] = router.get("save_to")
    cfg_router["mode"] = "handoff_end"
    cfg_router.setdefault("fallback_key", "general")
    cfg["router"] = cfg_router
    flow["config"] = cfg

    flow["blocks"] = blocks
    return {"flow": flow, "routes": routes}


def _normalize_to_flow(data: Any, *, filename: str, template: dict | None) -> dict[str, Any]:
    """
    Convierte inputs comunes (lista de bloques, bloque suelto, blocks como lista) a un flow completo.
    """
    tpl = template if isinstance(template, dict) else {}
    languages = tpl.get("languages") if isinstance(tpl.get("languages"), list) else ["es", "pt", "en", "ca"]
    languages = [str(x) for x in languages if x] or ["es"]
    plan = str(tpl.get("plan") or "base")
    config = tpl.get("config") if isinstance(tpl.get("config"), dict) else {}

    # Ya es un flow completo con blocks dict
    if isinstance(data, dict) and isinstance(data.get("blocks"), dict) and data.get("blocks"):
        out = dict(data)
        if not isinstance(out.get("start_block"), str) or not out.get("start_block"):
            out["start_block"] = (tpl.get("start_block") if isinstance(tpl.get("start_block"), str) else None) or next(iter(out["blocks"].keys()))
        if not isinstance(out.get("languages"), list) or not out.get("languages"):
            out["languages"] = languages
        if "config" not in out or not isinstance(out.get("config"), dict):
            out["config"] = config
        if "plan" not in out:
            out["plan"] = plan
        if "version" not in out:
            out["version"] = str(tpl.get("version") or filename.replace(".json", ""))
        return out

    blocks: dict[str, Any] = {}
    start_block: str | None = None

    # Flow con blocks list
    if isinstance(data, dict) and isinstance(data.get("blocks"), list):
        blocks = _normalize_blocks_list_to_dict(data.get("blocks") or [])
        start_block = data.get("start_block") if isinstance(data.get("start_block"), str) else None
    # Lista de bloques directamente
    elif isinstance(data, list):
        blocks = _normalize_blocks_list_to_dict(data)
    # Bloque suelto
    elif isinstance(data, dict) and ("id" in data and "type" in data):
        blocks = _normalize_blocks_list_to_dict([data])
        start_block = str(data.get("id") or "").strip() or None
    else:
        raise ValueError("formato_no_reconocido")

    if not blocks:
        raise ValueError("missing_blocks")

    # Elegir start_block: preferir template si existe en blocks, luego el del input, luego el primero.
    tpl_start = tpl.get("start_block") if isinstance(tpl.get("start_block"), str) else None
    if tpl_start and tpl_start in blocks:
        start_block = tpl_start
    if start_block and start_block in blocks:
        chosen_start = start_block
    else:
        chosen_start = next(iter(blocks.keys()))

    version = str(tpl.get("version") or filename.replace(".json", ""))
    return {
        "version": version,
        "plan": plan,
        "languages": languages,
        "start_block": chosen_start,
        "config": config,
        "blocks": blocks,
    }


def _json_editor(*, vertical_key: str, title: str, filename: str, value: dict, template: dict | None = None):
    state_key = f"_v_edit_{vertical_key}_{filename}"
    rev_key = f"{state_key}_rev"
    text_key = f"{state_key}_text"
    if rev_key not in st.session_state:
        st.session_state[rev_key] = 0
    if state_key not in st.session_state:
        st.session_state[state_key] = value or {}
    if text_key not in st.session_state:
        st.session_state[text_key] = json.dumps(st.session_state[state_key] or {}, ensure_ascii=False, indent=2)
    widget_key = f"{state_key}_ta_{st.session_state[rev_key]}"
    st.markdown(f"**{title}** (`{filename}`)")
    if _is_flow_filename(filename):
        st.caption(
            "Edición JSON (flow completo). Requiere `start_block` y `blocks` como objeto/dict (no lista)."
        )
    else:
        st.caption("Edición JSON.")
    c1, c2 = st.columns([0.6, 0.4])
    if template and write_enabled:
        if c2.button("Restaurar plantilla", key=f"{state_key}_reset", use_container_width=True):
            st.session_state[state_key] = template or {}
            st.session_state[text_key] = json.dumps(template or {}, ensure_ascii=False, indent=2)
            st.session_state[rev_key] = int(st.session_state.get(rev_key, 0) or 0) + 1
            st.rerun()
    if write_enabled and _is_flow_filename(filename):
        if c2.button("Normalizar a flow", key=f"{state_key}_normalize", use_container_width=True):
            try:
                candidate = json.loads(st.session_state.get(text_key) or "null")
                normalized = _normalize_to_flow(candidate, filename=filename, template=template)
            except Exception as exc:
                st.error(f"No se pudo normalizar: {exc}")
                return
            st.session_state[state_key] = normalized
            st.session_state[text_key] = json.dumps(normalized, ensure_ascii=False, indent=2)
            st.session_state[rev_key] = int(st.session_state.get(rev_key, 0) or 0) + 1
            st.success("Normalizado a flow completo.")
            st.rerun()
    upload = c2.file_uploader(f"Subir {filename}", type=["json"], key=f"{state_key}_up", disabled=not write_enabled)
    if upload is not None and write_enabled:
        try:
            parsed = json.loads(upload.getvalue().decode("utf-8"))
            st.session_state[state_key] = parsed if isinstance(parsed, dict) else parsed
            st.session_state[text_key] = json.dumps(st.session_state[state_key] or {}, ensure_ascii=False, indent=2)
            st.session_state[rev_key] = int(st.session_state.get(rev_key, 0) or 0) + 1
            st.success(f"{filename} cargado en el editor.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo leer JSON: {exc}")
            return

    txt = st.text_area(
        f"{filename} editor",
        value=str(st.session_state.get(text_key) or ""),
        key=widget_key,
        height=240,
        disabled=not write_enabled,
    )
    st.session_state[text_key] = txt
    if c1.button(f"Guardar {filename}", key=f"{state_key}_save", disabled=not write_enabled):
        try:
            data = json.loads(txt or "{}")
        except Exception as exc:
            st.error(f"JSON inválido: {exc}")
            return
        # Pre-validación amigable: evita el error típico "missing_blocks" por borrar la estructura.
        if _is_flow_filename(filename):
            if not isinstance(data, dict):
                st.error("Este archivo debe ser un objeto JSON (flow completo).")
                return
            if not isinstance(data.get("blocks"), dict) or not data.get("blocks"):
                st.error(
                    "Flow inválido: falta `blocks` (debe ser un objeto/dict con IDs de bloque como claves)."
                )
                return
            if not isinstance(data.get("start_block"), str) or not data.get("start_block"):
                st.error("Flow inválido: falta `start_block` (string).")
                return
        out = update_vertical_file_admin(
            ctx.token,
            vertical_key,
            filename,
            kind="json",
            content=data,
            validate=True,
            api_key=ctx.api_key,
        )
        if isinstance(out, dict) and out.get("error"):
            _show_api_error(out, f"No se pudo guardar {filename}")
        else:
            st.success(f"{filename} guardado.")
            st.session_state[state_key] = data if isinstance(data, dict) else st.session_state.get(state_key) or {}
            st.session_state.pop("_admin_vertical_catalog", None)
            st.rerun()


def _text_editor(*, vertical_key: str, title: str, filename: str, value: str):
    state_key = f"_v_edit_{vertical_key}_{filename}"
    widget_key = f"{state_key}_ta"
    if state_key not in st.session_state:
        st.session_state[state_key] = (value or "").strip()
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state[state_key]
    st.markdown(f"**{title}** (`{filename}`)")
    txt = st.text_area(
        f"{filename} editor",
        key=widget_key,
        height=240,
        disabled=not write_enabled,
    )
    c1, c2 = st.columns([0.6, 0.4])
    upload = c2.file_uploader(f"Subir {filename}", type=["txt"], key=f"{state_key}_up", disabled=not write_enabled)
    if upload is not None and write_enabled:
        try:
            content = upload.getvalue().decode("utf-8")
            st.session_state[state_key] = content
            st.session_state[widget_key] = content
            st.success(f"{filename} cargado en el editor.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo leer archivo: {exc}")
    if c1.button(f"Guardar {filename}", key=f"{state_key}_save", disabled=not write_enabled):
        out = update_vertical_file_admin(
            ctx.token,
            vertical_key,
            filename,
            kind="text",
            content=txt,
            validate=False,
            api_key=ctx.api_key,
        )
        if isinstance(out, dict) and out.get("error"):
            _show_api_error(out, f"No se pudo guardar {filename}")
        else:
            st.success(f"{filename} guardado.")
            st.session_state[state_key] = txt
            st.session_state.pop("_admin_vertical_catalog", None)
            st.rerun()


vertical_items, vertical_keys, vertical_labels, _ = ensure_vertical_catalog(ctx)
if not vertical_items:
    st.warning("No se han encontrado verticales.")
    vertical_items = []
    vertical_keys = []
    vertical_labels = {}

with st.expander("➕ Crear vertical", expanded=False):
    st.caption("Crea un vertical nuevo y su `flow_base.json` inicial (válido).")
    with st.form("create-vertical"):
        ck1, ck2 = st.columns([0.4, 0.6])
        new_key = ck1.text_input("Key (slug)", placeholder="ej: dental_clinics", disabled=not write_enabled)
        new_label = ck2.text_input("Label", placeholder="Nombre comercial", disabled=not write_enabled)
        default_flow_id = st.text_input("Default flow id", placeholder="ej: dental_clinics_base_v1", disabled=not write_enabled)
        flow_file = st.file_uploader("flow_base.json (opcional)", type=["json"], disabled=not write_enabled)
        submitted = st.form_submit_button("Crear", use_container_width=True, disabled=not write_enabled)
    if submitted:
        flow_base = None
        if flow_file is not None:
            try:
                import json as _json

                flow_base = _json.loads(flow_file.getvalue().decode("utf-8"))
            except Exception as exc:
                st.error(f"flow_base.json inválido: {exc}")
                flow_base = None
        payload = {
            "key": (new_key or "").strip(),
            "label": (new_label or "").strip() or None,
            "default_flow_id": (default_flow_id or "").strip() or None,
            "flow_base": flow_base,
        }
        res = create_vertical_admin(ctx.token, payload, api_key=ctx.api_key)
        if isinstance(res, dict) and res.get("error"):
            _show_api_error(res, "No se pudo crear el vertical")
        else:
            st.success("Vertical creado.")
            st.session_state.pop("_admin_vertical_catalog", None)
            st.rerun()

st.markdown("**Detalle de vertical**")
selected_key = st.selectbox(
    "Selecciona un vertical",
    vertical_keys or [],
    format_func=lambda v: vertical_labels.get(v, v),
    key="vertical-detail-select",
)
if selected_key:
    detail = get_vertical(ctx.token, selected_key, api_key=ctx.api_key) or {}
    if detail.get("error"):
        _show_api_error(detail, "No se pudo cargar el vertical")
    else:
        cfg = detail.get("config") if isinstance(detail.get("config"), dict) else {}
        assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
        files = detail.get("files") if isinstance(detail.get("files"), dict) else {}
        meta = assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {}

        st.markdown(f"**Key:** `{detail.get('key') or selected_key}`")
        promise = cfg.get("promise_commercial")
        if promise:
            st.caption(f"Promesa: {promise}")

        scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
        if not scope_defs:
            scope_defs = cfg.get("scope_definitions") if isinstance(cfg.get("scope_definitions"), dict) else {}
        scope_keys = sorted([str(k) for k in scope_defs.keys() if k])

        missing_assets = [fname for fname, ok in files.items() if not ok] if isinstance(files, dict) else []
        if missing_assets:
            st.warning(f"Faltan archivos mínimos del vertical: {', '.join(missing_assets)}")

        prompt_vertical_ok = bool((assets.get("prompt_vertical") or "").strip())
        scope_prompt_missing: list[str] = []
        scope_flow_base_missing: list[str] = []
        for sk in scope_keys:
            resp = read_vertical_file_admin(ctx.token, selected_key, f"prompt_scope_{sk}.txt", api_key=ctx.api_key)
            ok = isinstance(resp, dict) and isinstance(resp.get("content"), str) and bool((resp.get("content") or "").strip())
            if not ok:
                scope_prompt_missing.append(sk)
            resp_flow = read_vertical_file_admin(ctx.token, selected_key, f"flow_base_scope_{sk}.json", api_key=ctx.api_key)
            ok_flow = isinstance(resp_flow, dict) and isinstance(resp_flow.get("content"), dict) and bool(resp_flow.get("content"))
            if not ok_flow:
                scope_flow_base_missing.append(sk)

        if not prompt_vertical_ok:
            st.warning("Falta `prompt_vertical.txt` (base del vertical).")
        if scope_keys and scope_prompt_missing:
            st.warning(f"Faltan prompts por scope: {', '.join(scope_prompt_missing)}")
        if scope_keys and scope_flow_base_missing:
            st.warning(f"Faltan flow base por scope: {', '.join(scope_flow_base_missing)}")

        options = ["Overview", "Scopes", "Test IA"]
        section_key = st.radio(
            "Sección",
            options=options,
            horizontal=True,
            key=f"vertical-section-{selected_key}",
        )

        if section_key == "Overview":
            st.subheader("Overview")
            st.caption("Checklist mínimo para operar: prompt vertical + (por scope) prompt + flow base.")
            st.markdown("**Checklist (listo para generar)**")
            st.write(
                {
                    "prompt_vertical_ok": prompt_vertical_ok,
                    "scopes_defined": bool(scope_keys),
                    "scope_prompts_missing": scope_prompt_missing,
                    "scope_flow_base_missing": scope_flow_base_missing,
                    "vertical_files_missing": missing_assets,
                }
            )

        elif section_key == "Scopes":
            st.subheader("Scopes (sub-verticals)")
            st.caption("Cada scope tiene 1 prompt + 1 flow base (estructura). El tenant solo edita textos/labels.")

            items = []
            for sk in scope_keys:
                entry = scope_defs.get(sk) if isinstance(scope_defs.get(sk), dict) else {}
                label = entry.get("label") or sk
                items.append(
                    {
                        "key": sk,
                        "label": label,
                        "prompt": "OK" if sk not in scope_prompt_missing else "MISSING",
                        "flow_base": "OK" if sk not in scope_flow_base_missing else "MISSING",
                    }
                )
            if items:
                st.table(items)
            else:
                st.info("Este vertical no tiene scopes definidos todavía.")

            if write_enabled:
                with st.expander("➕ Crear scope + prompt (v2)", expanded=False):
                    with st.form(f"create-scope-{selected_key}"):
                        c1, c2 = st.columns([0.35, 0.65])
                        new_scope_key = c1.text_input("Scope key", placeholder="ej: reformas", max_chars=64)
                        new_scope_label = c2.text_input("Label", placeholder="Nombre visible (opcional)")
                        submitted = st.form_submit_button("Crear", use_container_width=True)
                    if submitted:
                        k = (new_scope_key or "").strip().lower()
                        if not k:
                            st.error("Scope key requerido.")
                        elif not _KEY_RE.match(k):
                            st.error("Scope key inválido. Usa minúsculas, números, _ o -, 2–63 caracteres.")
                        else:
                            meta2 = dict(meta) if isinstance(meta, dict) else {}
                            defs = meta2.get("scope_definitions")
                            if not isinstance(defs, dict):
                                defs = {}
                            if k in defs:
                                st.error("Ese scope ya existe.")
                            else:
                                defs[k] = {"label": (new_scope_label or "").strip() or k}
                                meta2["scope_definitions"] = defs
                                out = update_vertical_file_admin(
                                    ctx.token,
                                    selected_key,
                                    "metadata.json",
                                    kind="json",
                                    content=meta2,
                                    validate=True,
                                    api_key=ctx.api_key,
                                )
                                if isinstance(out, dict) and out.get("error"):
                                    _show_api_error(out, "No se pudo guardar metadata.json")
                                else:
                                    stub = (
                                        f"Scope: {k}\n"
                                        "Objetivo: describe la especialidad del negocio para este scope.\n"
                                        "Incluye: servicios, precios, horarios, materiales y políticas cuando aparezcan en los documentos.\n"
                                        "Estilo: claro, directo, orientado a captación y agenda.\n"
                                    )
                                    out2 = update_vertical_file_admin(
                                        ctx.token,
                                        selected_key,
                                        f"prompt_scope_{k}.txt",
                                        kind="text",
                                        content=stub,
                                        validate=False,
                                        api_key=ctx.api_key,
                                    )
                                    if isinstance(out2, dict) and out2.get("error"):
                                        _show_api_error(out2, f"No se pudo crear prompt_scope_{k}.txt")
                                    base_tpl = assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else {}
                                    base_flow = dict(base_tpl) if isinstance(base_tpl, dict) else {}
                                    if isinstance(base_flow, dict) and base_flow:
                                        base_flow["version"] = f"{selected_key}_{k}_base"
                                    out3 = update_vertical_file_admin(
                                        ctx.token,
                                        selected_key,
                                        f"flow_base_scope_{k}.json",
                                        kind="json",
                                        content=base_flow if isinstance(base_flow, dict) else {},
                                        validate=True,
                                        api_key=ctx.api_key,
                                    )
                                    if isinstance(out3, dict) and out3.get("error"):
                                        _show_api_error(out3, f"No se pudo crear flow_base_scope_{k}.json")
                                    st.success("Scope creado.")
                                    st.session_state.pop("_admin_vertical_catalog", None)
                                    st.rerun()

            st.divider()
            st.markdown("### Editor de scope")
            if not scope_keys:
                st.info("Primero crea scopes.")
            else:
                scope_sel = st.selectbox("Scope", options=scope_keys, key=f"scope-edit-select-{selected_key}")

                st.markdown("#### Prompt del scope")
                fname_prompt = f"prompt_scope_{scope_sel}.txt"
                existing_text = ""
                read_p = read_vertical_file_admin(ctx.token, selected_key, fname_prompt, api_key=ctx.api_key)
                if isinstance(read_p, dict) and isinstance(read_p.get("content"), str):
                    existing_text = read_p.get("content") or ""
                _text_editor(vertical_key=selected_key, title=f"prompt_scope {scope_sel}", filename=fname_prompt, value=existing_text)

                st.markdown("#### Flow base del scope (estructura)")
                fname_flow = f"flow_base_scope_{scope_sel}.json"
                existing_flow = {}
                read_f = read_vertical_file_admin(ctx.token, selected_key, fname_flow, api_key=ctx.api_key)
                if isinstance(read_f, dict) and isinstance(read_f.get("content"), dict):
                    existing_flow = read_f.get("content") or {}
                _json_editor(
                    vertical_key=selected_key,
                    title=f"flow_base_scope {scope_sel}",
                    filename=fname_flow,
                    value=existing_flow,
                    template=(assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else None),
                )

                st.markdown("#### Router + Subflows (v1-safe)")
                st.caption(
                    "Patrón recomendado: un bloque router (buttons/options) que clasifica y ramifica con `next_map` a subflows. "
                    "Sin `condition`, sin `internal`. El router termina en `end` y el motor carga el sub-flow (archivo) correspondiente."
                )
                if not write_enabled:
                    st.info("Modo solo lectura: scaffold de subflows deshabilitado.")
                else:
                    # Siempre operar sobre el flow guardado (no sobre el editor en memoria)
                    flow_live = existing_flow if isinstance(existing_flow, dict) else {}
                    blocks = flow_live.get("blocks") if isinstance(flow_live.get("blocks"), dict) else {}
                    router_candidates = [
                        bid
                        for bid, b in blocks.items()
                        if isinstance(b, dict)
                        and str(b.get("type") or "").strip().lower() in {"buttons", "options"}
                        and isinstance(b.get("options"), list)
                        and b.get("options")
                    ]
                    if not router_candidates:
                        st.warning("No se detectaron bloques buttons/options con `options` para usar como router.")
                    else:
                        cfg = flow_live.get("config") if isinstance(flow_live.get("config"), dict) else {}
                        cfg_router = cfg.get("router") if isinstance(cfg.get("router"), dict) else {}
                        default_router = cfg_router.get("block_id")
                        if default_router not in router_candidates:
                            default_router = router_candidates[0]
                        router_block_id = st.selectbox(
                            "Bloque router",
                            options=router_candidates,
                            index=router_candidates.index(default_router) if default_router in router_candidates else 0,
                            key=f"router-block-{selected_key}-{scope_sel}",
                        )
                        router_block = blocks.get(router_block_id) if isinstance(blocks.get(router_block_id), dict) else {}
                        default_save_to = str(router_block.get("save_to") or cfg_router.get("save_to") or "intent")
                        save_to = st.text_input(
                            "Guardar selección en (save_to)",
                            value=default_save_to,
                            key=f"router-save-to-{selected_key}-{scope_sel}",
                            help="Se guarda en vars para trazabilidad/analytics. El motor usa este valor para elegir el sub-flow.",
                        )
                        option_ids = [_option_id(o) for o in (router_block.get("options") or []) if _option_id(o)]
                        default_fallback = "otro" if "otro" in option_ids else (option_ids[0] if option_ids else "general")
                        fallback_key = st.text_input(
                            "Fallback (si no hay match)",
                            value=str(cfg_router.get("fallback_key") or default_fallback),
                            key=f"router-fallback-{selected_key}-{scope_sel}",
                            help="Si el usuario manda un valor inesperado, se usa este sub-flow por defecto.",
                        )
                        overwrite = st.checkbox(
                            "Sobrescribir sub-flows existentes (scaffold)",
                            value=False,
                            key=f"router-overwrite-{selected_key}-{scope_sel}",
                        )
                        c1, c2 = st.columns([0.6, 0.4])
                        if c1.button(
                            "Scaffold subflows desde opciones",
                            use_container_width=True,
                            key=f"router-scaffold-{selected_key}-{scope_sel}",
                        ):
                            try:
                                out = _scaffold_router_subflows(
                                    json.loads(json.dumps(flow_live)),
                                    router_block_id=str(router_block_id),
                                    save_to=str(save_to or "").strip() or "intent",
                                )
                            except Exception as exc:
                                st.error(f"No se pudo scaffold: {exc}")
                            else:
                                updated = out.get("flow") if isinstance(out, dict) else None
                                if not isinstance(updated, dict):
                                    st.error("Scaffold falló: payload inválido.")
                                else:
                                    # 1) Guardar flow router (termina en end) + metadata de router con routes_file
                                    routes_file = _routes_filename(scope_sel, str(save_to or "").strip() or "intent")
                                    updated.setdefault("config", {})
                                    if not isinstance(updated.get("config"), dict):
                                        updated["config"] = {}
                                    updated["config"]["router"] = {
                                        "block_id": str(router_block_id),
                                        "scope": str(scope_sel),
                                        "save_to": str(save_to or "").strip() or "intent",
                                        "mode": "handoff_end",
                                        "routes_file": routes_file,
                                        "fallback_key": _slugify_subflow_key(fallback_key) or "general",
                                    }
                                    res = update_vertical_file_admin(
                                        ctx.token,
                                        selected_key,
                                        fname_flow,
                                        kind="json",
                                        content=updated,
                                        validate=True,
                                        api_key=ctx.api_key,
                                    )
                                    if isinstance(res, dict) and res.get("error"):
                                        _show_api_error(res, "No se pudo guardar el flow tras scaffold")
                                    else:
                                        # 2) Crear sub-flows (archivos) + 3) Crear routes file (mapeo)
                                        routes = out.get("routes") if isinstance(out, dict) else None
                                        if not isinstance(routes, dict) or not routes:
                                            st.error("No se pudieron derivar rutas del router.")
                                            st.stop()

                                        # Construir mapping a archivos de subflow
                                        route_entries: dict[str, dict[str, str]] = {}
                                        for opt_id, sub_key in routes.items():
                                            if not opt_id or not sub_key:
                                                continue
                                            # Buscar label humano del option
                                            lbl = None
                                            for o in (router_block.get("options") or []):
                                                if _option_id(o) == str(opt_id):
                                                    if isinstance(o, dict):
                                                        l = o.get("label") or o.get("text") or opt_id
                                                        lbl = str(l) if not isinstance(l, dict) else str(next(iter(l.values()), opt_id))
                                                    else:
                                                        lbl = str(o)
                                                    break
                                            sf_file = _subflow_filename(scope_sel, str(save_to or "").strip() or "intent", str(sub_key))
                                            sf_id = _subflow_flow_id(
                                                vertical_key=selected_key,
                                                scope_key=scope_sel,
                                                save_to=str(save_to or "").strip() or "intent",
                                                subflow_key=str(sub_key),
                                            )
                                            route_entries[str(opt_id)] = {"subflow_id": sf_id, "file": sf_file}

                                            # Crear/actualizar subflow file
                                            existing_sf = read_vertical_file_admin(ctx.token, selected_key, sf_file, api_key=ctx.api_key)
                                            exists = isinstance(existing_sf, dict) and isinstance(existing_sf.get("content"), dict)
                                            should_write = bool(overwrite or not exists)
                                            if should_write:
                                                sf_flow = _subflow_skeleton(
                                                    vertical_key=selected_key,
                                                    scope_key=scope_sel,
                                                    save_to=str(save_to or "").strip() or "intent",
                                                    subflow_key=str(sub_key),
                                                    label=lbl,
                                                    template_flow=updated,
                                                )
                                                out_sf = update_vertical_file_admin(
                                                    ctx.token,
                                                    selected_key,
                                                    sf_file,
                                                    kind="json",
                                                    content=sf_flow,
                                                    validate=True,
                                                    api_key=ctx.api_key,
                                                )
                                                if isinstance(out_sf, dict) and out_sf.get("error"):
                                                    _show_api_error(out_sf, f"No se pudo crear {sf_file}")

                                        routes_payload = {
                                            "router": {"block_id": str(router_block_id), "save_to": str(save_to or "").strip() or "intent", "scope": scope_sel},
                                            "routes": route_entries,
                                            "default": route_entries.get(_slugify_subflow_key(fallback_key) or str(default_fallback)) or next(iter(route_entries.values())),
                                        }
                                        out_routes = update_vertical_file_admin(
                                            ctx.token,
                                            selected_key,
                                            routes_file,
                                            kind="json",
                                            content=routes_payload,
                                            validate=False,
                                            api_key=ctx.api_key,
                                        )
                                        if isinstance(out_routes, dict) and out_routes.get("error"):
                                            _show_api_error(out_routes, f"No se pudo guardar {routes_file}")
                                        st.success(f"Router actualizado + sub-flows listos. Archivo de rutas: `{routes_file}`.")
                                        st.rerun()

                        if c2.button(
                            "Marcar como router (solo metadata)",
                            use_container_width=True,
                            key=f"router-mark-{selected_key}-{scope_sel}",
                        ):
                            try:
                                updated = json.loads(json.dumps(flow_live))
                                updated.setdefault("config", {})
                                if not isinstance(updated["config"], dict):
                                    updated["config"] = {}
                                routes_file = _routes_filename(scope_sel, str(save_to or "").strip() or "intent")
                                updated["config"]["router"] = {
                                    "block_id": str(router_block_id),
                                    "scope": str(scope_sel),
                                    "save_to": str(save_to or "").strip() or "intent",
                                    "mode": "handoff_end",
                                    "routes_file": routes_file,
                                    "fallback_key": _slugify_subflow_key(fallback_key) or "general",
                                }
                                res = update_vertical_file_admin(
                                    ctx.token,
                                    selected_key,
                                    fname_flow,
                                    kind="json",
                                    content=updated,
                                    validate=True,
                                    api_key=ctx.api_key,
                                )
                                if isinstance(res, dict) and res.get("error"):
                                    _show_api_error(res, "No se pudo guardar metadata de router")
                                else:
                                    st.success("Router metadata guardada. Recargando…")
                                    st.rerun()
                            except Exception as exc:
                                st.error(f"No se pudo guardar metadata: {exc}")

                    # Sub-flows del scope: colección abierta (independiente del router)
                    st.markdown("#### Sub-flows del scope (colección abierta)")
                    st.caption(
                        "El scope es dueño de los sub-flows. El router solo referencia una `key` (guardada en `save_to`). "
                        "Los sub-flows pueden existir aunque el router no los use todavía."
                    )

                    subflows_save_to_default = str(cfg_router.get("save_to") or router_block.get("save_to") or "intent")
                    subflows_save_to = st.text_input(
                        "save_to (colección de sub-flows)",
                        value=subflows_save_to_default,
                        key=f"sf-save-to-{selected_key}-{scope_sel}",
                        help="Agrupa sub-flows por variable de router. Puedes crear sub-flows aunque el router todavía no exista.",
                    )
                    save_to_norm = str(subflows_save_to or "").strip().lower() or "intent"
                    files_payload = list_vertical_files_admin(ctx.token, selected_key, api_key=ctx.api_key)
                    files_items = files_payload.get("items") if isinstance(files_payload, dict) else None
                    if not isinstance(files_items, list):
                        _show_api_error(files_payload, "No se pudieron listar archivos del vertical")
                        files_items = []

                    subflow_files_by_key: dict[str, str] = {}
                    for it in files_items:
                        if not isinstance(it, dict):
                            continue
                        sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
                        if not isinstance(sf, dict):
                            continue
                        if str(sf.get("scope") or "").strip().lower() != str(scope_sel).strip().lower():
                            continue
                        if str(sf.get("save_to") or "").strip().lower() != save_to_norm:
                            continue
                        k = _slugify_subflow_key(sf.get("key"))
                        fname = str(it.get("normalized_filename") or it.get("filename") or "").strip()
                        if k and fname:
                            subflow_files_by_key.setdefault(k, fname)

                    # Cobertura: keys que el router podría emitir
                    router_option_keys = [
                        _slugify_subflow_key(_option_id(o))
                        for o in (router_block.get("options") or [])
                        if _option_id(o)
                    ]
                    router_option_keys = [k for k in router_option_keys if k]
                    missing_for_router = [k for k in router_option_keys if k not in subflow_files_by_key]
                    if router_option_keys:
                        st.caption(
                            f"Keys en opciones del router: {len(router_option_keys)} · "
                            f"sub-flows existentes: {len(subflow_files_by_key)} · "
                            f"faltan: {len(missing_for_router)}"
                        )

                    c_new1, c_new2, c_new3 = st.columns([0.35, 0.45, 0.2])
                    new_key = c_new1.text_input(
                        "Nueva key",
                        value="",
                        key=f"sf-new-key-{selected_key}-{scope_sel}",
                        help="Identificador del sub-flow (ej: `implantes`).",
                    )
                    new_label = c_new2.text_input(
                        "Label (opcional)",
                        value="",
                        key=f"sf-new-label-{selected_key}-{scope_sel}",
                    )
                    if c_new3.button(
                        "Crear sub-flow",
                        use_container_width=True,
                        key=f"sf-new-create-{selected_key}-{scope_sel}",
                    ):
                        try:
                            sub_key = _slugify_subflow_key(new_key)
                            sf_file = _subflow_filename(scope_sel, save_to_norm, sub_key)
                            existing_sf = read_vertical_file_admin(ctx.token, selected_key, sf_file, api_key=ctx.api_key)
                            exists = isinstance(existing_sf, dict) and isinstance(existing_sf.get("content"), dict)
                            if exists:
                                st.warning(f"Ya existe: `{sf_file}`")
                            else:
                                sf_flow = _subflow_skeleton(
                                    vertical_key=selected_key,
                                    scope_key=scope_sel,
                                    save_to=save_to_norm,
                                    subflow_key=sub_key,
                                    label=new_label.strip() or None,
                                    template_flow=flow_live,
                                )
                                out_sf = update_vertical_file_admin(
                                    ctx.token,
                                    selected_key,
                                    sf_file,
                                    kind="json",
                                    content=sf_flow,
                                    validate=True,
                                    api_key=ctx.api_key,
                                )
                                if isinstance(out_sf, dict) and out_sf.get("error"):
                                    _show_api_error(out_sf, f"No se pudo crear {sf_file}")
                                else:
                                    st.success(f"Sub-flow creado: `{sf_file}`")
                                    st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo crear sub-flow: {exc}")

                    upload_sf = st.file_uploader(
                        "Subir JSON de sub-flow (flow completo)",
                        type=["json"],
                        key=f"sf-upload-{selected_key}-{scope_sel}",
                        disabled=not write_enabled,
                    )
                    if upload_sf is not None and write_enabled:
                        try:
                            parsed = json.loads(upload_sf.getvalue().decode("utf-8"))
                            sub_key = _slugify_subflow_key(new_key or "general")
                            sf_file = _subflow_filename(scope_sel, save_to_norm, sub_key)
                            normalized = _normalize_to_flow(parsed, filename=sf_file, template=flow_live)
                            normalized.setdefault("config", {})
                            if not isinstance(normalized.get("config"), dict):
                                normalized["config"] = {}
                            normalized["config"] = dict(normalized.get("config") or {})
                            normalized["config"]["subflow"] = {
                                "vertical_key": str(selected_key),
                                "scope": str(scope_sel),
                                "router_save_to": str(save_to_norm),
                                "key": str(sub_key),
                                "label": (new_label or "").strip() or None,
                            }
                            out_sf = update_vertical_file_admin(
                                ctx.token,
                                selected_key,
                                sf_file,
                                kind="json",
                                content=normalized,
                                validate=True,
                                api_key=ctx.api_key,
                            )
                            if isinstance(out_sf, dict) and out_sf.get("error"):
                                _show_api_error(out_sf, f"No se pudo guardar {sf_file}")
                            else:
                                st.success(f"Sub-flow subido: `{sf_file}`")
                                st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo subir sub-flow: {exc}")

                    sf_keys = sorted(subflow_files_by_key.keys())
                    if not sf_keys:
                        st.info("No hay sub-flows para este scope/save_to todavía.")
                    else:
                        sf_choice_key = st.selectbox(
                            "Sub-flow",
                            options=sf_keys,
                            key=f"sf-scope-select-{selected_key}-{scope_sel}",
                            format_func=lambda k: f"{k} → {subflow_files_by_key.get(k)}",
                        )
                        sf_file = subflow_files_by_key.get(sf_choice_key)
                        if sf_file:
                            sf_read = read_vertical_file_admin(ctx.token, selected_key, str(sf_file), api_key=ctx.api_key)
                            sf_flow = sf_read.get("content") if isinstance(sf_read, dict) and isinstance(sf_read.get("content"), dict) else {}
                            _json_editor(
                                vertical_key=selected_key,
                                title=f"subflow {sf_choice_key}",
                                filename=str(sf_file),
                                value=sf_flow,
                                template=None,
                            )

                            c_del1, c_del2 = st.columns([0.7, 0.3])
                            confirm = c_del1.checkbox(
                                f"Confirmar borrado de `{sf_file}`",
                                value=False,
                                key=f"sf-del-confirm-{selected_key}-{scope_sel}-{sf_choice_key}",
                                disabled=not write_enabled,
                            )
                            if c_del2.button(
                                "Borrar sub-flow",
                                use_container_width=True,
                                key=f"sf-del-{selected_key}-{scope_sel}-{sf_choice_key}",
                                disabled=not write_enabled or not confirm,
                            ):
                                res_del = delete_vertical_file_admin(ctx.token, selected_key, str(sf_file), api_key=ctx.api_key)
                                if isinstance(res_del, dict) and res_del.get("error"):
                                    _show_api_error(res_del, f"No se pudo borrar {sf_file}")
                                else:
                                    st.success(f"Sub-flow borrado: `{sf_file}`")
                                    st.rerun()

                    # Editor de subflows (si hay routes_file)
                    try:
                        flow_cfg = flow_live.get("config") if isinstance(flow_live.get("config"), dict) else {}
                        router_meta = flow_cfg.get("router") if isinstance(flow_cfg.get("router"), dict) else {}
                        routes_file = router_meta.get("routes_file")
                        if routes_file:
                            routes_payload = read_vertical_file_admin(ctx.token, selected_key, str(routes_file), api_key=ctx.api_key)
                            if isinstance(routes_payload, dict) and isinstance(routes_payload.get("content"), dict):
                                content = routes_payload["content"]
                                route_entries = content.get("routes") if isinstance(content.get("routes"), dict) else {}
                                if route_entries:
                                    st.markdown("#### Sub-flows del router")
                                    ids = list(route_entries.keys())
                                    sf_choice = st.selectbox(
                                        "Opción (router) → sub-flow",
                                        options=ids,
                                        format_func=lambda k: f"{k} → {(route_entries.get(k) or {}).get('subflow_id') or (route_entries.get(k) or {}).get('file')}",
                                        key=f"sf-select-{selected_key}-{scope_sel}",
                                    )
                                    entry = route_entries.get(sf_choice) if isinstance(route_entries.get(sf_choice), dict) else {}
                                    sf_file = entry.get("file")
                                    if sf_file:
                                        sf_read = read_vertical_file_admin(ctx.token, selected_key, str(sf_file), api_key=ctx.api_key)
                                        sf_flow = sf_read.get("content") if isinstance(sf_read, dict) and isinstance(sf_read.get("content"), dict) else {}
                                        _json_editor(
                                            vertical_key=selected_key,
                                            title=f"subflow {sf_choice}",
                                            filename=str(sf_file),
                                            value=sf_flow,
                                            template=None,
                                        )
                    except Exception:
                        pass

        else:
            st.subheader("Test IA (admin)")
            st.caption("Prueba la generación (preview/dry-run o real) para validar prompts. En producción, el tenant genera su draft.")

            _text_editor(vertical_key=selected_key, title="prompt_vertical", filename="prompt_vertical.txt", value=assets.get("prompt_vertical") or "")
            _text_editor(
                vertical_key=selected_key,
                title="prompt_vertical_extension",
                filename="prompt_vertical_extension.txt",
                value=assets.get("prompt_vertical_extension") or "",
            )

            st.divider()
            st.markdown("### Test de generación (admin)")
            test_mode = st.radio(
                "Modo",
                options=["Dry-run (preview prompt)", "Real (llama IA)"],
                horizontal=True,
                key=f"gen-mode-{selected_key}",
            )
            test_scopes = st.multiselect(
                "Scopes usados en el test",
                options=scope_keys,
                default=scope_keys,
                key=f"gen-scopes-{selected_key}",
            )
            test_langs = st.multiselect(
                "Idiomas",
                options=["es", "pt", "en", "ca"],
                default=["es", "pt", "en", "ca"],
                key=f"gen-langs-{selected_key}",
            )
            tenant_name = st.text_input("Nombre de tenant (opcional)", value="", key=f"gen-tenant-name-{selected_key}")
            business_knowledge = st.text_area(
                "Business knowledge (opcional, texto de ejemplo)",
                value="",
                height=140,
                key=f"gen-kb-{selected_key}",
            )

            model = None
            temperature = 0.3
            if test_mode.startswith("Real"):
                c1, c2 = st.columns([0.6, 0.4])
                model = c1.selectbox(
                    "Modelo (opcional)",
                    options=["(default)", "gpt-4o-mini", "gpt-4o"],
                    index=0,
                    key=f"gen-model-{selected_key}",
                )
                temperature = float(
                    c2.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.3,
                        step=0.05,
                        key=f"gen-temp-{selected_key}",
                    )
                )
                if model == "(default)":
                    model = None

            if st.button("Ejecutar test", use_container_width=True, key=f"gen-run-{selected_key}"):
                payload = {
                    "mode": "real" if test_mode.startswith("Real") else "dry",
                    "scopes": list(test_scopes or []),
                    "languages": list(test_langs or []),
                    "tenant_name": tenant_name.strip() or None,
                    "business_knowledge": business_knowledge.strip() or None,
                    "model": model,
                    "temperature": temperature,
                }
                payload = {k: v for k, v in payload.items() if v is not None}
                with st.spinner("Ejecutando…"):
                    res = preview_vertical_flow_generator(ctx.token, selected_key, payload, api_key=ctx.api_key)
                if isinstance(res, dict) and res.get("error"):
                    _show_api_error(res, "No se pudo ejecutar el test")
                else:
                    st.success("OK")
                    st.code(res.get("system_message") or "", language="text")
                    st.json(res.get("user_prompt") or {})
                    if isinstance(res.get("flow"), dict) and res.get("flow"):
                        st.subheader("Flow (sanitized)")
                        st.json(res.get("flow") or {})
                        with st.expander("Raw (debug)", expanded=False):
                            st.json(res.get("patch") or {})

st.divider()
st.subheader("Lista")
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
