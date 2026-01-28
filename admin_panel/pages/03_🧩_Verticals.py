import sys
from pathlib import Path
import json
import re
from typing import Any

import streamlit as st

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
from admin_panel.ui import (
    can_write,
    ensure_vertical_catalog,
    init_page,
    render_impersonation_banner,
    render_sidebar_nav,
    require_admin_context,
)

init_page(title="SuperAdmin — Verticals", icon="🧩")

ctx = require_admin_context()
render_sidebar_nav()
render_impersonation_banner()

# -----------------------------------------------------------------------------
# Config + helpers
# -----------------------------------------------------------------------------

_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")
_SUBFLOW_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,30}$")

write_enabled = can_write(ctx) and not st.session_state.get("impersonation_token")
if not write_enabled:
    st.info("Modo solo lectura: edición/creación desactivada.")


def _show_api_error(payload: object, fallback: str) -> None:
    if isinstance(payload, dict) and payload.get("error"):
        st.error(f"{fallback} (HTTP {payload.get('status_code', 'N/A')}): {payload.get('error')}")


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
        "end_block": "end",
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


def _subflow_template_blocks(template_key: str, label: str | None) -> dict[str, Any] | None:
    title = (label or "").strip() or template_key.replace("_", " ").title()
    if template_key == "intro_welcome":
        return {
            "intro": {"id": "intro", "type": "message", "text": f"Bienvenida: {title}", "next": "ready"},
            "ready": {
                "id": "ready",
                "type": "buttons",
                "text": "¿Empezamos ahora?",
                "options": [{"label": "Sí", "value": "yes"}, {"label": "No ahora", "value": "no"}],
                "save_to": "ready",
                "next_map": {"yes": "end", "no": "end"},
            },
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "question_buttons":
        return {
            "intro": {
                "id": "intro",
                "type": "buttons",
                "text": f"{title}: elige una opción",
                "options": [{"label": "Opción A", "value": "a"}, {"label": "Opción B", "value": "b"}],
                "save_to": "choice",
                "next": "end",
            },
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "question_input":
        return {
            "intro": {"id": "intro", "type": "input", "text": f"{title}: escribe tu respuesta", "save_to": "input_value", "next": "end"},
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "contact_capture":
        return {
            "contact_name": {"id": "contact_name", "type": "input", "text": "¿Cuál es tu nombre?", "save_to": "contact_name", "next": "contact_phone"},
            "contact_phone": {"id": "contact_phone", "type": "input", "text": "¿Cuál es tu teléfono?", "save_to": "contact_phone", "next": "end"},
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "budget":
        return {
            "budget": {
                "id": "budget",
                "type": "buttons",
                "text": "¿Cuál es tu presupuesto aproximado?",
                "options": [{"label": "<5k", "value": "<5k"}, {"label": "5-15k", "value": "5-15k"}, {"label": ">15k", "value": ">15k"}],
                "save_to": "budget",
                "next": "end",
            },
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "urgency":
        return {
            "urgency": {
                "id": "urgency",
                "type": "buttons",
                "text": "¿Qué urgencia tiene?",
                "options": [{"label": "Alta", "value": "alta"}, {"label": "Media", "value": "media"}, {"label": "Baja", "value": "baja"}],
                "save_to": "urgency",
                "next": "end",
            },
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "appointment_offer":
        return {
            "appointment_offer": {
                "id": "appointment_offer",
                "type": "message",
                "text": "Podemos agendar una primera cita.",
                "next": "end",
            },
            "end": {"id": "end", "type": "end"},
        }
    if template_key == "closing":
        return {
            "closing": {"id": "closing", "type": "message", "text": "Gracias. ¡Hasta pronto!", "next": "end"},
            "end": {"id": "end", "type": "end"},
        }
    return None


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

    if end_block_id not in blocks:
        blocks[end_block_id] = {"id": end_block_id, "type": "end"}

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

    router["next"] = end_block_id

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
    tpl = template if isinstance(template, dict) else {}
    languages = tpl.get("languages") if isinstance(tpl.get("languages"), list) else ["es", "pt", "en", "ca"]
    languages = [str(x) for x in languages if x] or ["es"]
    plan = str(tpl.get("plan") or "base")
    config = tpl.get("config") if isinstance(tpl.get("config"), dict) else {}

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

    if isinstance(data, dict) and isinstance(data.get("blocks"), list):
        blocks = _normalize_blocks_list_to_dict(data.get("blocks") or [])
        start_block = data.get("start_block") if isinstance(data.get("start_block"), str) else None
    elif isinstance(data, list):
        blocks = _normalize_blocks_list_to_dict(data)
    elif isinstance(data, dict) and ("id" in data and "type" in data):
        blocks = _normalize_blocks_list_to_dict([data])
        start_block = str(data.get("id") or "").strip() or None
    else:
        raise ValueError("formato_no_reconocido")

    if not blocks:
        raise ValueError("missing_blocks")

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


def _json_editor(
    *,
    vertical_key: str,
    title: str,
    filename: str,
    value: dict,
    template: dict | None = None,
    instance_key: str | None = None,
):
    state_key = f"_v_edit_{vertical_key}_{filename}"
    suffix = instance_key or state_key
    rev_key = f"{state_key}_rev"
    text_key = f"{state_key}_text"
    if rev_key not in st.session_state:
        st.session_state[rev_key] = 0
    if state_key not in st.session_state:
        st.session_state[state_key] = value or {}
    if text_key not in st.session_state:
        st.session_state[text_key] = json.dumps(st.session_state[state_key] or {}, ensure_ascii=False, indent=2)
    widget_key = f"{state_key}_ta_{suffix}_{st.session_state[rev_key]}"
    st.markdown(f"**{title}** (`{filename}`)")
    if _is_flow_filename(filename):
        st.caption("Edición JSON (flow completo). Requiere `start_block` y `blocks` como objeto/dict.")
    else:
        st.caption("Edición JSON.")
    c1, c2 = st.columns([0.6, 0.4])
    if template and write_enabled:
        if c2.button("Restaurar plantilla", key=f"{state_key}_{suffix}_reset", use_container_width=True):
            st.session_state[state_key] = template or {}
            st.session_state[text_key] = json.dumps(template or {}, ensure_ascii=False, indent=2)
            st.session_state[rev_key] = int(st.session_state.get(rev_key, 0) or 0) + 1
            st.rerun()
    if write_enabled and _is_flow_filename(filename):
        if c2.button("Normalizar a flow", key=f"{state_key}_{suffix}_normalize", use_container_width=True):
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
    upload = c2.file_uploader(
        f"Subir {filename}", type=["json"], key=f"{state_key}_{suffix}_up", disabled=not write_enabled
    )
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
    if c1.button(f"Guardar {filename}", key=f"{state_key}_{suffix}_save", disabled=not write_enabled):
        try:
            data = json.loads(txt or "{}")
        except Exception as exc:
            st.error(f"JSON inválido: {exc}")
            return
        if _is_flow_filename(filename):
            if not isinstance(data, dict):
                st.error("Este archivo debe ser un objeto JSON (flow completo).")
                return
            if not isinstance(data.get("blocks"), dict) or not data.get("blocks"):
                st.error("Flow inválido: falta `blocks` (objeto con IDs de bloque).")
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


def _text_editor(
    *,
    vertical_key: str,
    title: str,
    filename: str,
    value: str,
    instance_key: str | None = None,
):
    state_key = f"_v_edit_{vertical_key}_{filename}"
    suffix = instance_key or state_key
    widget_key = f"{state_key}_ta"
    if state_key not in st.session_state:
        st.session_state[state_key] = (value or "").strip()
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state[state_key]
    st.markdown(f"**{title}** (`{filename}`)")
    txt = st.text_area(
        f"{filename} editor",
        key=f"{widget_key}_{suffix}",
        height=240,
        disabled=not write_enabled,
    )
    c1, c2 = st.columns([0.6, 0.4])
    upload = c2.file_uploader(
        f"Subir {filename}", type=["txt"], key=f"{state_key}_{suffix}_up", disabled=not write_enabled
    )
    if upload is not None and write_enabled:
        try:
            content = upload.getvalue().decode("utf-8")
            st.session_state[state_key] = content
            st.session_state[widget_key] = content
            st.success(f"{filename} cargado en el editor.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo leer archivo: {exc}")
    if c1.button(f"Guardar {filename}", key=f"{state_key}_{suffix}_save", disabled=not write_enabled):
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


# -----------------------------------------------------------------------------
# UI state helpers
# -----------------------------------------------------------------------------


def _get_catalog():
    vertical_items, vertical_keys, vertical_labels, _ = ensure_vertical_catalog(ctx)
    if not vertical_items:
        return [], [], {}
    return vertical_items, vertical_keys, vertical_labels


def _search_filter(items: list[dict[str, Any]], term: str) -> list[dict[str, Any]]:
    if not term:
        return items
    needle = term.strip().lower()
    out = []
    for v in items:
        if not isinstance(v, dict):
            continue
        key = str(v.get("key") or "").lower()
        label = str(v.get("label") or "").lower()
        scope_items = v.get("scope_items") if isinstance(v.get("scope_items"), list) else []
        scope_join = " ".join([str(s.get("label") or s.get("key") or "") for s in scope_items]).lower()
        hay = " ".join([key, label, scope_join])
        if needle in hay:
            out.append(v)
    return out


def _vertical_counts(v: dict[str, Any]) -> tuple[int, int, str]:
    scopes = v.get("scope_items") if isinstance(v.get("scope_items"), list) else []
    scopes_count = len(scopes)
    flow_ids = v.get("flow_ids") if isinstance(v.get("flow_ids"), list) else []
    flow_count = len(flow_ids) if flow_ids else (1 if v.get("flow_template_exists") else 0)
    flow_count = max(flow_count, scopes_count + (1 if v.get("flow_template_exists") else 0))
    files = v.get("files") if isinstance(v.get("files"), dict) else {}
    missing = [f for f, ok in files.items() if not ok]
    status = "Atención" if missing else "OK"
    return scopes_count, flow_count, status


def _ensure_selected_vertical(items: list[dict[str, Any]]):
    selected = st.session_state.get("vertical_selected")
    keys = [str(v.get("key")) for v in items if v.get("key")]
    if selected in keys:
        return selected
    if keys:
        st.session_state["vertical_selected"] = keys[0]
        return keys[0]
    return None


# -----------------------------------------------------------------------------
# Header + guide
# -----------------------------------------------------------------------------


def render_header(items: list[dict[str, Any]], vertical_labels: dict[str, str]):
    st.title("Verticales")
    st.caption("Define plantillas base: vertical → scopes → flows → subflows")

    c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
    st.session_state["verticals_search"] = c1.text_input(
        "Buscar",
        value=st.session_state.get("verticals_search", ""),
        placeholder="Buscar por vertical, scope o guion",
    )

    choices = ["Todos"] + [str(v.get("key")) for v in items if v.get("key")]
    current_filter = st.session_state.get("verticals_filter", "Todos")
    if current_filter not in choices:
        current_filter = "Todos"
    selection = c2.selectbox(
        "Filtrar vertical",
        options=choices,
        index=choices.index(current_filter),
        format_func=lambda k: "Todos" if k == "Todos" else vertical_labels.get(k, k),
    )
    st.session_state["verticals_filter"] = selection

    st.session_state["verticals_show_advanced"] = c3.toggle(
        "Mostrar opciones avanzadas",
        value=bool(st.session_state.get("verticals_show_advanced")),
    )

    with st.expander("Guía rápida", expanded=False):
        st.markdown(
            """
- Crea la **Plantilla principal** (Vertical)
- Añade **Contextos/Alcances** (Scopes)
- Define **Guiones** (Flows)
- Añade **Subguiones** (Subflows) cuando quieras modularizar
            """
        )


# -----------------------------------------------------------------------------
# Wizard
# -----------------------------------------------------------------------------


def _wizard_init():
    st.session_state.setdefault("vertical_wizard", {})
    wiz = st.session_state["vertical_wizard"]
    wiz.setdefault("step", 1)
    wiz.setdefault("basic", {"key": "", "label": "", "description": "", "default_flow_id": ""})
    wiz.setdefault("scopes", [])
    wiz.setdefault("subflows", [])
    wiz.setdefault("advanced", {"flow_base": None, "prompt_vertical": "", "prompt_extension": ""})
    return wiz


def _wizard_reset():
    st.session_state["vertical_wizard"] = {
        "step": 1,
        "basic": {"key": "", "label": "", "description": "", "default_flow_id": ""},
        "scopes": [],
        "subflows": [],
        "advanced": {"flow_base": None, "prompt_vertical": "", "prompt_extension": ""},
    }


def _wizard_add_scope(wiz: dict[str, Any], key: str, label: str):
    k = (key or "").strip().lower()
    if not k:
        st.error("Falta el key del scope.")
        return
    if not _KEY_RE.match(k):
        st.error("Scope inválido. Usa minúsculas, números, _ o -.")
        return
    existing = [s["key"] for s in wiz.get("scopes", [])]
    if k in existing:
        st.warning("Ese scope ya está en la lista.")
        return
    wiz.setdefault("scopes", []).append({"key": k, "label": (label or "").strip() or k})


def _wizard_add_subflow(wiz: dict[str, Any], scope: str, save_to: str, key: str, label: str, template_key: str):
    scope_key = (scope or "").strip().lower() or "default"
    save_to = (save_to or "").strip().lower() or "intent"
    sub_key = _slugify_subflow_key(key)
    if not sub_key:
        st.error("Falta key de subguion.")
        return
    wiz.setdefault("subflows", []).append(
        {
            "scope": scope_key,
            "save_to": save_to,
            "key": sub_key,
            "label": (label or "").strip() or sub_key,
            "template": template_key,
        }
    )


def _wizard_step_header(step: int, total: int = 3):
    st.markdown(f"### Paso {step} de {total}")


def render_wizard_create_vertical():
    wiz = _wizard_init()
    step = int(wiz.get("step", 1))

    st.markdown("## Crear plantilla principal")
    st.caption("Un flujo guiado para crear un vertical con sus contextos y guiones.")

    _wizard_step_header(step)

    if step == 1:
        with st.form("wizard-step-1"):
            c1, c2 = st.columns([0.5, 0.5])
            wiz["basic"]["key"] = c1.text_input("Slug (key)", value=wiz["basic"].get("key", ""))
            wiz["basic"]["label"] = c2.text_input("Nombre visible", value=wiz["basic"].get("label", ""))
            wiz["basic"]["description"] = st.text_area(
                "Descripción corta",
                value=wiz["basic"].get("description", ""),
                height=80,
            )
            if st.session_state.get("verticals_show_advanced"):
                wiz["basic"]["default_flow_id"] = st.text_input(
                    "Default flow id (avanzado)",
                    value=wiz["basic"].get("default_flow_id", ""),
                )
                flow_file = st.file_uploader("flow_base.json (opcional)", type=["json"], key="wizard-flow-base")
                if flow_file is not None:
                    try:
                        wiz["advanced"]["flow_base"] = json.loads(flow_file.getvalue().decode("utf-8"))
                    except Exception as exc:
                        st.error(f"flow_base.json inválido: {exc}")
                wiz["advanced"]["prompt_vertical"] = st.text_area(
                    "Prompt vertical (opcional)",
                    value=wiz["advanced"].get("prompt_vertical", ""),
                    height=80,
                )
                wiz["advanced"]["prompt_extension"] = st.text_area(
                    "Extensión de prompt (opcional)",
                    value=wiz["advanced"].get("prompt_extension", ""),
                    height=80,
                )
            submitted = st.form_submit_button("Siguiente", use_container_width=True)
        if submitted:
            k = wiz["basic"].get("key", "").strip().lower()
            if not k or not _KEY_RE.match(k):
                st.error("Slug inválido. Usa minúsculas, números, _ o -.")
                return
            if not wiz["basic"].get("label", "").strip():
                st.error("Falta el nombre visible.")
                return
            wiz["step"] = 2
            st.rerun()

    elif step == 2:
        st.markdown("**Contextos / Alcances (Scopes)**")
        st.caption("Define 1 o más contextos donde se usará el guion.")

        c1, c2, c3 = st.columns([0.4, 0.4, 0.2])
        scope_key = c1.text_input("Key", value="", key="wiz-scope-key")
        scope_label = c2.text_input("Label", value="", key="wiz-scope-label")
        if c3.button("Agregar", use_container_width=True):
            _wizard_add_scope(wiz, scope_key, scope_label)

        scopes = wiz.get("scopes", [])
        if scopes:
            for idx, s in enumerate(scopes):
                cols = st.columns([0.6, 0.3, 0.1])
                cols[0].write(f"{s['key']} — {s['label']}")
                if cols[2].button("✕", key=f"wiz-scope-del-{idx}"):
                    wiz["scopes"].pop(idx)
                    st.rerun()
        else:
            st.info("Aún no añadiste scopes. Puedes avanzar si tu vertical no los necesita.")

        c_prev, c_next = st.columns([0.5, 0.5])
        if c_prev.button("Atrás", use_container_width=True):
            wiz["step"] = 1
            st.rerun()
        if c_next.button("Siguiente", use_container_width=True):
            wiz["step"] = 3
            st.rerun()

    elif step == 3:
        st.markdown("**Guiones y subguiones**")
        st.caption("Define subguiones opcionales por scope (si aplica).")

        scopes = wiz.get("scopes", [])
        scope_options = [s["key"] for s in scopes] or ["default"]
        c1, c2, c3, c4 = st.columns([0.25, 0.2, 0.2, 0.35])
        sf_scope = c1.selectbox("Scope", options=scope_options, key="wiz-sf-scope")
        sf_save_to = c2.text_input("save_to", value="intent", key="wiz-sf-save")
        sf_key = c3.text_input("key", value="", key="wiz-sf-key")
        sf_label = c4.text_input("label", value="", key="wiz-sf-label")

        template_options = [
            "blank",
            "intro_welcome",
            "question_buttons",
            "question_input",
            "contact_capture",
            "budget",
            "urgency",
            "appointment_offer",
            "closing",
        ]
        template_key = st.selectbox("Plantilla", options=template_options, index=0, key="wiz-sf-tpl")
        if st.button("Agregar subguion", use_container_width=True):
            _wizard_add_subflow(wiz, sf_scope, sf_save_to, sf_key, sf_label, template_key)

        subflows = wiz.get("subflows", [])
        if subflows:
            for idx, sf in enumerate(subflows):
                cols = st.columns([0.7, 0.2, 0.1])
                cols[0].write(f"{sf['scope']} / {sf['save_to']} → {sf['key']} ({sf['label']})")
                cols[1].write(sf.get("template") or "blank")
                if cols[2].button("✕", key=f"wiz-sf-del-{idx}"):
                    wiz["subflows"].pop(idx)
                    st.rerun()
        else:
            st.info("No añadiste subguiones (opcional).")

        c_prev, c_save = st.columns([0.5, 0.5])
        if c_prev.button("Atrás", use_container_width=True):
            wiz["step"] = 2
            st.rerun()
        if c_save.button("Crear vertical", use_container_width=True, disabled=not write_enabled):
            basic = wiz.get("basic", {})
            payload = {
                "key": (basic.get("key") or "").strip(),
                "label": (basic.get("label") or "").strip() or None,
                "default_flow_id": (basic.get("default_flow_id") or "").strip() or None,
                "flow_base": wiz.get("advanced", {}).get("flow_base"),
            }
            payload = {k: v for k, v in payload.items() if v not in (None, "")}
            with st.spinner("Creando vertical..."):
                res = create_vertical_admin(ctx.token, payload, api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                _show_api_error(res, "No se pudo crear el vertical")
                return

            vkey = payload["key"].lower()
            # metadata.json extras (description + scopes)
            meta_payload = read_vertical_file_admin(ctx.token, vkey, "metadata.json", api_key=ctx.api_key)
            meta_content = meta_payload.get("content") if isinstance(meta_payload, dict) and isinstance(meta_payload.get("content"), dict) else {}
            if basic.get("description"):
                meta_content["description"] = basic.get("description")
            if scopes:
                defs = meta_content.get("scope_definitions") if isinstance(meta_content.get("scope_definitions"), dict) else {}
                for s in scopes:
                    defs[s["key"]] = {"label": s.get("label") or s["key"]}
                meta_content["scope_definitions"] = defs
                out_meta = update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    "metadata.json",
                    kind="json",
                    content=meta_content,
                    validate=True,
                    api_key=ctx.api_key,
                )
                if isinstance(out_meta, dict) and out_meta.get("error"):
                    _show_api_error(out_meta, "No se pudo guardar metadata")

            # prompts base (si no existen, crear stub)
            if wiz.get("advanced", {}).get("prompt_vertical"):
                update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    "prompt_vertical.txt",
                    kind="text",
                    content=wiz.get("advanced", {}).get("prompt_vertical") or "",
                    validate=False,
                    api_key=ctx.api_key,
                )
            if wiz.get("advanced", {}).get("prompt_extension"):
                update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    "prompt_vertical_extension.txt",
                    kind="text",
                    content=wiz.get("advanced", {}).get("prompt_extension") or "",
                    validate=False,
                    api_key=ctx.api_key,
                )

            # crear scope assets (prompt + flow_base_scope)
            for s in scopes:
                sk = s["key"]
                stub = (
                    f"Scope: {sk}\n"
                    "Objetivo: describe la especialidad del negocio para este scope.\n"
                    "Incluye: servicios, precios, horarios, materiales y políticas cuando aparezcan en los documentos.\n"
                    "Estilo: claro, directo, orientado a captación y agenda.\n"
                )
                update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    f"prompt_scope_{sk}.txt",
                    kind="text",
                    content=stub,
                    validate=False,
                    api_key=ctx.api_key,
                )
                base_tpl = res.get("assets", {}).get("flow_base") if isinstance(res, dict) else None
                base_flow = dict(base_tpl) if isinstance(base_tpl, dict) else {}
                if isinstance(base_flow, dict) and base_flow:
                    base_flow["version"] = f"{vkey}_{sk}_base"
                update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    f"flow_base_scope_{sk}.json",
                    kind="json",
                    content=base_flow if isinstance(base_flow, dict) else {},
                    validate=True,
                    api_key=ctx.api_key,
                )

            # crear subflows
            for sf in wiz.get("subflows", []):
                scope_key = sf.get("scope") or "default"
                save_to = sf.get("save_to") or "intent"
                sub_key = sf.get("key") or "general"
                sf_file = _subflow_filename(scope_key, save_to, sub_key)
                sf_flow = _subflow_skeleton(
                    vertical_key=vkey,
                    scope_key=scope_key,
                    save_to=save_to,
                    subflow_key=sub_key,
                    label=sf.get("label"),
                    template_flow=wiz.get("advanced", {}).get("flow_base") or res.get("assets", {}).get("flow_base") if isinstance(res, dict) else None,
                )
                tpl_key = sf.get("template")
                if tpl_key and tpl_key != "blank":
                    tpl_blocks = _subflow_template_blocks(tpl_key, sf.get("label"))
                    if isinstance(tpl_blocks, dict):
                        sf_flow["blocks"] = tpl_blocks
                        for bid in tpl_blocks.keys():
                            if bid != "end":
                                sf_flow["start_block"] = bid
                                break
                        sf_flow["end_block"] = "end"
                update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    sf_file,
                    kind="json",
                    content=sf_flow,
                    validate=True,
                    api_key=ctx.api_key,
                )

            st.success("Vertical creado.")
            st.session_state.pop("_admin_vertical_catalog", None)
            st.session_state["vertical_selected"] = vkey
            st.session_state["verticals_show_wizard"] = False
            _wizard_reset()
            st.rerun()


# -----------------------------------------------------------------------------
# Left column: vertical list
# -----------------------------------------------------------------------------


def render_vertical_list(items: list[dict[str, Any]], vertical_labels: dict[str, str]):
    st.markdown("### Lista de verticales")
    if st.button("+ Crear vertical", use_container_width=True, disabled=not write_enabled):
        st.session_state["verticals_show_wizard"] = True

    if not items:
        st.info("No se encontraron verticales.")
        return

    selected = st.session_state.get("vertical_selected")

    for v in items:
        key = str(v.get("key") or "")
        label = str(v.get("label") or key)
        scopes_count, flows_count, status = _vertical_counts(v)
        is_active = key == selected

        box = st.container()
        with box:
            c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
            c1.markdown(f"**{label}**")
            c1.caption(key)
            c2.write(f"Scopes: {scopes_count}")
            c2.write(f"Guiones: {flows_count}")
            c3.write(status)

            a1, a2, a3 = st.columns([0.34, 0.33, 0.33])
            if a1.button("Editar", key=f"select-{key}", use_container_width=True):
                st.session_state["vertical_selected"] = key
                st.session_state["verticals_show_wizard"] = False
                st.rerun()
            if a2.button("Duplicar", key=f"dup-{key}", use_container_width=True, disabled=not write_enabled):
                st.session_state["verticals_dup_target"] = key
            if a3.button("Eliminar", key=f"del-{key}", use_container_width=True, disabled=not write_enabled):
                st.session_state["verticals_delete_target"] = key

        if is_active:
            st.session_state["vertical_selected"] = key

    # Duplicate form
    dup_key = st.session_state.get("verticals_dup_target")
    if dup_key:
        st.divider()
        st.markdown("#### Duplicar vertical")
        with st.form("dup-vertical-form"):
            new_key = st.text_input("Nuevo slug (key)")
            new_label = st.text_input("Nuevo nombre visible")
            submitted = st.form_submit_button("Duplicar", use_container_width=True)
        if submitted:
            if not new_key or not _KEY_RE.match(new_key.strip().lower()):
                st.error("Slug inválido para el duplicado.")
            else:
                with st.spinner("Duplicando..."):
                    source = get_vertical(ctx.token, dup_key, api_key=ctx.api_key) or {}
                    if source.get("error"):
                        _show_api_error(source, "No se pudo cargar el vertical fuente")
                        return
                    payload = {
                        "key": new_key.strip().lower(),
                        "label": (new_label or "").strip() or f"{vertical_labels.get(dup_key, dup_key)} (Copia)",
                        "default_flow_id": source.get("config", {}).get("default_flow_id"),
                        "flow_base": source.get("assets", {}).get("flow_base"),
                    }
                    res = create_vertical_admin(ctx.token, payload, api_key=ctx.api_key)
                    if isinstance(res, dict) and res.get("error"):
                        _show_api_error(res, "No se pudo duplicar el vertical")
                        return
                    # copiar archivos adicionales
                    files_payload = list_vertical_files_admin(ctx.token, dup_key, api_key=ctx.api_key)
                    files_items = files_payload.get("items") if isinstance(files_payload, dict) else []
                    for it in files_items:
                        fname = str(it.get("normalized_filename") or it.get("filename") or "").strip()
                        if fname in {"metadata.json", "flow_base.json"}:
                            continue
                        file_data = read_vertical_file_admin(ctx.token, dup_key, fname, api_key=ctx.api_key)
                        content = file_data.get("content") if isinstance(file_data, dict) else None
                        kind = file_data.get("kind") if isinstance(file_data, dict) else "json"
                        if content is None:
                            continue
                        update_vertical_file_admin(
                            ctx.token,
                            new_key.strip().lower(),
                            fname,
                            kind=str(kind or "json"),
                            content=content,
                            validate=False,
                            api_key=ctx.api_key,
                        )
                st.success("Duplicado creado.")
                st.session_state.pop("_admin_vertical_catalog", None)
                st.session_state["verticals_dup_target"] = None
                st.rerun()

    # Delete form (note: API does not delete registry; removes files only)
    del_key = st.session_state.get("verticals_delete_target")
    if del_key:
        st.divider()
        st.markdown("#### Eliminar vertical (confirmación)")
        st.caption("Esta acción elimina los archivos del vertical. La entrada de registry puede permanecer.")
        confirm = st.text_input("Escribe ELIMINAR para confirmar", value="")
        if st.button("Eliminar definitivamente", use_container_width=True):
            if confirm.strip().upper() != "ELIMINAR":
                st.error("Confirmación incorrecta.")
            else:
                with st.spinner("Eliminando archivos del vertical..."):
                    files_payload = list_vertical_files_admin(ctx.token, del_key, api_key=ctx.api_key)
                    files_items = files_payload.get("items") if isinstance(files_payload, dict) else []
                    for it in files_items:
                        fname = str(it.get("normalized_filename") or it.get("filename") or "").strip()
                        if not fname:
                            continue
                        delete_vertical_file_admin(ctx.token, del_key, fname, api_key=ctx.api_key)
                st.success("Archivos del vertical eliminados.")
                st.session_state.pop("_admin_vertical_catalog", None)
                st.session_state["verticals_delete_target"] = None
                st.rerun()


# -----------------------------------------------------------------------------
# Right column: details
# -----------------------------------------------------------------------------


def _load_vertical_detail(selected_key: str) -> dict[str, Any] | None:
    if not selected_key:
        return None
    detail = get_vertical(ctx.token, selected_key, api_key=ctx.api_key) or {}
    if detail.get("error"):
        _show_api_error(detail, "No se pudo cargar el vertical")
        return None
    return detail


def _resolve_scope_defs(detail: dict[str, Any]) -> dict[str, Any]:
    cfg = detail.get("config") if isinstance(detail.get("config"), dict) else {}
    assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
    meta = assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {}
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    if not scope_defs:
        scope_defs = cfg.get("scope_definitions") if isinstance(cfg.get("scope_definitions"), dict) else {}
    return scope_defs


def _write_metadata(vertical_key: str, meta_content: dict[str, Any]):
    out = update_vertical_file_admin(
        ctx.token,
        vertical_key,
        "metadata.json",
        kind="json",
        content=meta_content,
        validate=True,
        api_key=ctx.api_key,
    )
    if isinstance(out, dict) and out.get("error"):
        _show_api_error(out, "No se pudo guardar metadata")
        return False
    st.session_state.pop("_admin_vertical_catalog", None)
    return True


def render_vertical_detail(detail: dict[str, Any]):
    selected_key = detail.get("key")
    cfg = detail.get("config") if isinstance(detail.get("config"), dict) else {}
    assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
    files = detail.get("files") if isinstance(detail.get("files"), dict) else {}
    meta = assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {}
    scope_defs = _resolve_scope_defs(detail)
    scope_keys = sorted([str(k) for k in scope_defs.keys() if k])

    st.markdown("### Detalle de vertical")
    st.markdown(f"**Plantilla principal:** {cfg.get('label') or selected_key}")
    if cfg.get("promise_commercial"):
        st.caption(f"Promesa: {cfg.get('promise_commercial')}")

    missing_assets = [fname for fname, ok in files.items() if not ok] if isinstance(files, dict) else []
    if missing_assets:
        st.warning(f"Faltan archivos mínimos: {', '.join(missing_assets)}")

    tab_resumen, tab_scopes, tab_flows = st.tabs(["Resumen", "Scopes", "Flows"])

    with tab_resumen:
        c1, c2, c3 = st.columns([0.34, 0.33, 0.33])
        c1.metric("Vertical", cfg.get("label") or selected_key)
        c2.metric("Scopes", len(scope_keys))
        c3.metric("Guiones", len(scope_keys) + (1 if files.get("flow_base.json") else 0))

        cta1, cta2 = st.columns([0.5, 0.5])
        if cta1.button("Crear scope", use_container_width=True):
            st.session_state["verticals_focus_tab"] = "scopes"
        if cta2.button("Crear flow", use_container_width=True):
            st.session_state["verticals_focus_tab"] = "flows"

        st.markdown("#### Últimos cambios")
        st.info("Sin datos de auditoría disponibles.")

        if st.session_state.get("verticals_show_advanced"):
            st.divider()
            st.markdown("#### Textos base (avanzado)")
            _text_editor(
                vertical_key=selected_key,
                title="prompt_vertical",
                filename="prompt_vertical.txt",
                value=assets.get("prompt_vertical") or "",
                instance_key=f"{selected_key}__prompt_vertical.txt",
            )
            _text_editor(
                vertical_key=selected_key,
                title="prompt_vertical_extension",
                filename="prompt_vertical_extension.txt",
                value=assets.get("prompt_vertical_extension") or "",
                instance_key=f"{selected_key}__prompt_vertical_extension.txt",
            )

    with tab_scopes:
        st.markdown("#### Contextos / Alcances")
        st.caption("Cada scope tiene su prompt y un flow base propio.")

        if scope_keys:
            for sk in scope_keys:
                entry = scope_defs.get(sk) if isinstance(scope_defs.get(sk), dict) else {}
                cols = st.columns([0.5, 0.25, 0.25])
                cols[0].write(f"{entry.get('label') or sk}")
                if cols[1].button("Editar", key=f"scope-edit-{selected_key}-{sk}"):
                    st.session_state["scope_edit_key"] = sk
                if cols[2].button("Eliminar", key=f"scope-del-{selected_key}-{sk}", disabled=not write_enabled):
                    st.session_state["scope_delete_key"] = sk
        else:
            st.info("No hay scopes aún.")

        st.divider()
        st.markdown("#### Crear scope")
        with st.form(f"create-scope-{selected_key}"):
            c1, c2 = st.columns([0.35, 0.65])
            new_scope_key = c1.text_input("Key", placeholder="ej: reformas", max_chars=64)
            new_scope_label = c2.text_input("Label", placeholder="Nombre visible (opcional)")
            submitted = st.form_submit_button("Crear scope", use_container_width=True, disabled=not write_enabled)
        if submitted:
            k = (new_scope_key or "").strip().lower()
            if not k:
                st.error("Scope key requerido.")
            elif not _KEY_RE.match(k):
                st.error("Scope key inválido. Usa minúsculas, números, _ o -, 2–63 caracteres.")
            else:
                meta2 = dict(meta) if isinstance(meta, dict) else {}
                defs = meta2.get("scope_definitions") if isinstance(meta2.get("scope_definitions"), dict) else {}
                if k in defs:
                    st.error("Ese scope ya existe.")
                else:
                    defs[k] = {"label": (new_scope_label or "").strip() or k}
                    meta2["scope_definitions"] = defs
                    if _write_metadata(selected_key, meta2):
                        stub = (
                            f"Scope: {k}\n"
                            "Objetivo: describe la especialidad del negocio para este scope.\n"
                            "Incluye: servicios, precios, horarios, materiales y políticas cuando aparezcan en los documentos.\n"
                            "Estilo: claro, directo, orientado a captación y agenda.\n"
                        )
                        update_vertical_file_admin(
                            ctx.token,
                            selected_key,
                            f"prompt_scope_{k}.txt",
                            kind="text",
                            content=stub,
                            validate=False,
                            api_key=ctx.api_key,
                        )
                        base_tpl = assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else {}
                        base_flow = dict(base_tpl) if isinstance(base_tpl, dict) else {}
                        if isinstance(base_flow, dict) and base_flow:
                            base_flow["version"] = f"{selected_key}_{k}_base"
                        update_vertical_file_admin(
                            ctx.token,
                            selected_key,
                            f"flow_base_scope_{k}.json",
                            kind="json",
                            content=base_flow if isinstance(base_flow, dict) else {},
                            validate=True,
                            api_key=ctx.api_key,
                        )
                        st.success("Scope creado.")
                        st.rerun()

        # Edit scope
        edit_key = st.session_state.get("scope_edit_key")
        if edit_key:
            st.divider()
            st.markdown(f"#### Editar scope: {edit_key}")
            with st.form(f"edit-scope-{selected_key}-{edit_key}"):
                label_val = (scope_defs.get(edit_key) or {}).get("label") or edit_key
                new_label = st.text_input("Label", value=label_val)
                saved = st.form_submit_button("Guardar", use_container_width=True, disabled=not write_enabled)
            if saved:
                meta2 = dict(meta) if isinstance(meta, dict) else {}
                defs = meta2.get("scope_definitions") if isinstance(meta2.get("scope_definitions"), dict) else {}
                if edit_key in defs:
                    defs[edit_key]["label"] = new_label
                    meta2["scope_definitions"] = defs
                    if _write_metadata(selected_key, meta2):
                        st.success("Scope actualizado.")
                        st.session_state.pop("scope_edit_key", None)
                        st.rerun()

        del_key = st.session_state.get("scope_delete_key")
        if del_key:
            st.divider()
            st.markdown(f"#### Eliminar scope: {del_key}")
            confirm = st.text_input("Escribe ELIMINAR para confirmar", key=f"scope-del-confirm-{selected_key}")
            if st.button("Eliminar scope", use_container_width=True, disabled=not write_enabled):
                if confirm.strip().upper() != "ELIMINAR":
                    st.error("Confirmación incorrecta.")
                else:
                    meta2 = dict(meta) if isinstance(meta, dict) else {}
                    defs = meta2.get("scope_definitions") if isinstance(meta2.get("scope_definitions"), dict) else {}
                    defs.pop(del_key, None)
                    meta2["scope_definitions"] = defs
                    if _write_metadata(selected_key, meta2):
                        # borrar archivos relacionados (best-effort)
                        for fname in [f"prompt_scope_{del_key}.txt", f"flow_base_scope_{del_key}.json"]:
                            delete_vertical_file_admin(ctx.token, selected_key, fname, api_key=ctx.api_key)
                        st.success("Scope eliminado.")
                        st.session_state.pop("scope_delete_key", None)
                        st.rerun()

        if st.session_state.get("verticals_show_advanced") and scope_keys:
            st.divider()
            st.markdown("#### Editor avanzado de scope")
            scope_sel = st.selectbox("Scope", options=scope_keys, key=f"scope-edit-select-{selected_key}")
            st.markdown("**Prompt del scope**")
            fname_prompt = f"prompt_scope_{scope_sel}.txt"
            existing_text = ""
            read_p = read_vertical_file_admin(ctx.token, selected_key, fname_prompt, api_key=ctx.api_key)
            if isinstance(read_p, dict) and isinstance(read_p.get("content"), str):
                existing_text = read_p.get("content") or ""
            _text_editor(
                vertical_key=selected_key,
                title=f"prompt_scope {scope_sel}",
                filename=fname_prompt,
                value=existing_text,
                instance_key=f"{selected_key}__{scope_sel}__{fname_prompt}",
            )

            st.markdown("**Flow base del scope**")
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
                instance_key=f"{selected_key}__{scope_sel}__{fname_flow}__scopes_editor",
            )

    with tab_flows:
        st.markdown("#### Guiones (Flows) y subguiones")
        st.caption("Organiza el guion base y los subguiones por scope.")

        # Flow base (global)
        with st.expander("Guion base (Flow) — flow_base.json", expanded=False):
            st.write("Guion principal del vertical.")
            if st.session_state.get("verticals_show_advanced"):
                _json_editor(
                    vertical_key=selected_key,
                    title="flow_base",
                    filename="flow_base.json",
                    value=assets.get("flow_base") or {},
                    template=assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else None,
                    instance_key=f"{selected_key}__flow_base.json",
                )

        # Flows por scope + subflows
        files_payload = list_vertical_files_admin(ctx.token, selected_key, api_key=ctx.api_key)
        files_items = files_payload.get("items") if isinstance(files_payload, dict) else []

        subflow_files_by_scope: dict[str, dict[str, str]] = {}
        for it in files_items:
            if not isinstance(it, dict):
                continue
            sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
            if not isinstance(sf, dict):
                continue
            scope = str(sf.get("scope") or "")
            save_to = str(sf.get("save_to") or "")
            key = _slugify_subflow_key(sf.get("key"))
            fname = str(it.get("normalized_filename") or it.get("filename") or "").strip()
            if scope and save_to and key and fname:
                subflow_files_by_scope.setdefault(scope, {})[f"{save_to}::{key}"] = fname

        for sk in scope_keys:
            with st.expander(f"Guion de scope: {sk}", expanded=False):
                fname_flow = f"flow_base_scope_{sk}.json"
                st.caption("Guion específico del scope.")
                if st.session_state.get("verticals_show_advanced"):
                    existing_flow = {}
                    read_f = read_vertical_file_admin(ctx.token, selected_key, fname_flow, api_key=ctx.api_key)
                    if isinstance(read_f, dict) and isinstance(read_f.get("content"), dict):
                        existing_flow = read_f.get("content") or {}
                    _json_editor(
                        vertical_key=selected_key,
                        title=f"flow_base_scope {sk}",
                        filename=fname_flow,
                        value=existing_flow,
                        template=(assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else None),
                        instance_key=f"{selected_key}__{sk}__{fname_flow}__flows_tab",
                    )

                st.markdown("**Subguiones (Subflows)**")
                scope_sf = subflow_files_by_scope.get(sk, {})
                if not scope_sf:
                    st.info("No hay subguiones para este scope.")
                else:
                    for label, fname in scope_sf.items():
                        cols = st.columns([0.7, 0.15, 0.15])
                        cols[0].write(label)
                        if cols[1].button("Editar", key=f"sf-edit-{sk}-{label}"):
                            st.session_state["sf_edit_file"] = fname
                        if cols[2].button("Eliminar", key=f"sf-del-{sk}-{label}", disabled=not write_enabled):
                            st.session_state["sf_delete_file"] = fname

                # Subflow actions
                if st.session_state.get("sf_edit_file") and st.session_state.get("verticals_show_advanced"):
                    sf_file = st.session_state.get("sf_edit_file")
                    sf_read = read_vertical_file_admin(ctx.token, selected_key, sf_file, api_key=ctx.api_key)
                    sf_flow = sf_read.get("content") if isinstance(sf_read, dict) and isinstance(sf_read.get("content"), dict) else {}
                    _json_editor(
                        vertical_key=selected_key,
                        title=f"subflow {sf_file}",
                        filename=str(sf_file),
                        value=sf_flow,
                        template=None,
                        instance_key=f"{selected_key}__{sf_file}",
                    )

                sf_del = st.session_state.get("sf_delete_file")
                if sf_del:
                    confirm = st.text_input("Escribe ELIMINAR para borrar subguion", key=f"sf-del-confirm-{sk}")
                    if st.button("Eliminar subguion", use_container_width=True, disabled=not write_enabled):
                        if confirm.strip().upper() != "ELIMINAR":
                            st.error("Confirmación incorrecta.")
                        else:
                            res_del = delete_vertical_file_admin(ctx.token, selected_key, sf_del, api_key=ctx.api_key)
                            if isinstance(res_del, dict) and res_del.get("error"):
                                _show_api_error(res_del, f"No se pudo borrar {sf_del}")
                            else:
                                st.success(f"Subguion borrado: {sf_del}")
                                st.session_state.pop("sf_delete_file", None)
                                st.rerun()

                if st.session_state.get("verticals_show_advanced"):
                    st.divider()
                    st.markdown("**Crear subguion (avanzado)**")
                    template_options = [
                        "blank",
                        "intro_welcome",
                        "question_buttons",
                        "question_input",
                        "contact_capture",
                        "budget",
                        "urgency",
                        "appointment_offer",
                        "closing",
                    ]
                    template_key = st.selectbox(
                        "Plantilla",
                        options=template_options,
                        index=0,
                        key=f"sf-template-{selected_key}-{sk}",
                    )
                    c_new1, c_new2, c_new3 = st.columns([0.35, 0.45, 0.2])
                    new_key = c_new1.text_input(
                        "Nueva key",
                        value="",
                        key=f"sf-new-key-{selected_key}-{sk}",
                    )
                    new_label = c_new2.text_input(
                        "Label (opcional)",
                        value="",
                        key=f"sf-new-label-{selected_key}-{sk}",
                    )
                    save_to_norm = "intent"
                    if c_new3.button(
                        "Crear subguion",
                        use_container_width=True,
                        key=f"sf-new-create-{selected_key}-{sk}",
                    ):
                        try:
                            sub_key = _slugify_subflow_key(new_key)
                            sf_file = _subflow_filename(sk, save_to_norm, sub_key)
                            existing_sf = read_vertical_file_admin(ctx.token, selected_key, sf_file, api_key=ctx.api_key)
                            exists = isinstance(existing_sf, dict) and isinstance(existing_sf.get("content"), dict)
                            if exists:
                                st.warning(f"Ya existe: `{sf_file}`")
                            else:
                                sf_flow = _subflow_skeleton(
                                    vertical_key=selected_key,
                                    scope_key=sk,
                                    save_to=save_to_norm,
                                    subflow_key=sub_key,
                                    label=new_label.strip() or None,
                                    template_flow=assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else None,
                                )
                                if template_key and template_key != "blank":
                                    tpl_blocks = _subflow_template_blocks(template_key, new_label.strip() or sub_key)
                                    if isinstance(tpl_blocks, dict):
                                        sf_flow["blocks"] = tpl_blocks
                                        for bid in tpl_blocks.keys():
                                            if bid != "end":
                                                sf_flow["start_block"] = bid
                                                break
                                        sf_flow["end_block"] = "end"
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
                                    st.success(f"Subguion creado: `{sf_file}`")
                                    st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo crear subguion: {exc}")

        if st.session_state.get("verticals_show_advanced"):
            st.divider()
            st.markdown("#### Test IA (avanzado)")
            st.caption("Prueba la generación para validar prompts. En producción, el tenant genera su draft.")
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
                "Business knowledge (opcional)",
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
                with st.spinner("Ejecutando..."):
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


# -----------------------------------------------------------------------------
# Main layout
# -----------------------------------------------------------------------------

vertical_items, vertical_keys, vertical_labels = _get_catalog()
render_header(vertical_items, vertical_labels)

# Filter + search
items = vertical_items
filter_key = st.session_state.get("verticals_filter")
if filter_key and filter_key != "Todos":
    items = [v for v in items if str(v.get("key")) == str(filter_key)]
items = _search_filter(items, st.session_state.get("verticals_search", ""))
selected_key = _ensure_selected_vertical(items)

left, right = st.columns([0.3, 0.7], gap="large")

with left:
    render_vertical_list(items, vertical_labels)

with right:
    if st.session_state.get("verticals_show_wizard"):
        render_wizard_create_vertical()
    elif not selected_key:
        st.info("Selecciona un vertical para ver el detalle.")
    else:
        detail = _load_vertical_detail(selected_key)
        if detail:
            render_vertical_detail(detail)
