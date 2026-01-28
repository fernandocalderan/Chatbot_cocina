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
from admin_panel.verticals_schema import (
    ValidationIssue,
    normalize_problem,
    validate_flow,
    validate_metadata,
    validate_problem,
)

init_page(title="🧩 Verticals", icon="🧩")

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


def _render_validation_issues(issues: list[ValidationIssue], *, title: str = "Validación") -> bool:
    if not issues:
        return True
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level != "error"]
    if errors:
        st.error(f"{title}: {len(errors)} errores")
        for it in errors:
            st.write(f"- {it.message}")
    if warnings:
        st.warning(f"{title}: {len(warnings)} advertencias")
        for it in warnings:
            st.write(f"- {it.message}")
    return not errors


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
    problem: dict[str, Any] | None = None,
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
    if isinstance(problem, dict):
        cfg["problem"] = problem
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
                "text": f"Problema: {label or subflow_key} (pendiente de configurar).",
                "next": "details",
            },
            "details": {
                "id": "details",
                "type": "input",
                "text": "Cuéntanos un poco más para ayudarte mejor.",
                "save_to": "problem_details",
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


def _build_linear_flow(*, steps: list[str], version: str, languages: list[str] | None = None) -> dict[str, Any]:
    langs = [str(x) for x in (languages or ["es"]) if x] or ["es"]
    clean_steps = [str(s).strip() for s in (steps or []) if str(s).strip()]
    if not clean_steps:
        clean_steps = ["Bienvenido. Empecemos con unas preguntas rápidas."]
    blocks: dict[str, Any] = {}
    ids: list[str] = []
    for idx, text in enumerate(clean_steps, start=1):
        bid = f"step_{idx}"
        ids.append(bid)
        blocks[bid] = {"id": bid, "type": "message", "text": text}
    blocks["end"] = {"id": "end", "type": "end"}
    for idx, bid in enumerate(ids):
        nxt = ids[idx + 1] if idx + 1 < len(ids) else "end"
        blocks[bid]["next"] = nxt
    return {
        "version": version,
        "plan": "base",
        "languages": langs,
        "start_block": ids[0],
        "config": {"ia_enabled": True, "ia_generation_level": 0, "pdf_enabled": False},
        "blocks": blocks,
    }


def _minimal_flow_router(*, version: str, languages: list[str] | None = None) -> dict[str, Any]:
    langs = [str(x) for x in (languages or ["es"]) if x] or ["es"]
    return {
        "version": version,
        "plan": "base",
        "languages": langs,
        "start_block": "welcome",
        "config": {"ia_enabled": True, "ia_generation_level": 0, "pdf_enabled": False},
        "blocks": {
            "welcome": {
                "id": "welcome",
                "type": "message",
                "text": "Hola. Vamos a definir tu caso rápidamente.",
                "next": "router",
            },
            "router": {
                "id": "router",
                "type": "buttons",
                "text": "¿Qué tema deseas tratar?",
                "options": [{"label": "General", "value": "general"}],
                "save_to": "topic",
                "next": "end",
            },
            "end": {"id": "end", "type": "end"},
        },
    }


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
        st.caption("Edición JSON (flow completo). Requiere `start_block` y `blocks` como objeto/dict.")
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


# -----------------------------------------------------------------------------
# Data loaders
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


def _ensure_selection(items: list[dict[str, Any]]):
    sel = st.session_state.get("knowledge_selection") or {}
    if sel.get("vertical"):
        return sel
    if items:
        st.session_state["knowledge_selection"] = {"type": "vertical", "vertical": items[0].get("key")}
        return st.session_state["knowledge_selection"]
    return {}


def _load_vertical_detail(selected_key: str) -> dict[str, Any] | None:
    if not selected_key:
        return None
    detail = get_vertical(ctx.token, selected_key, api_key=ctx.api_key) or {}
    if detail.get("error"):
        _show_api_error(detail, "No se pudo cargar la plantilla")
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
    ok = _render_validation_issues(validate_metadata(meta_content), title="Metadata")
    if not ok:
        return False
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


# -----------------------------------------------------------------------------
# Header + guide
# -----------------------------------------------------------------------------


def render_header(items: list[dict[str, Any]], vertical_labels: dict[str, str]):
    st.title("🧩 Verticals")
    st.caption("Editor de Conocimiento Conversacional · Plantilla → Especialidades → Guiones → Problemas")

    c1, c2, c3 = st.columns([0.5, 0.3, 0.2])
    st.session_state["knowledge_search"] = c1.text_input(
        "Buscar",
        value=st.session_state.get("knowledge_search", ""),
        placeholder="Buscar por plantilla, especialidad o guion",
    )

    choices = ["Todos"] + [str(v.get("key")) for v in items if v.get("key")]
    current_filter = st.session_state.get("knowledge_filter", "Todos")
    if current_filter not in choices:
        current_filter = "Todos"
    selection = c2.selectbox(
        "Filtrar plantilla",
        options=choices,
        index=choices.index(current_filter),
        format_func=lambda k: "Todos" if k == "Todos" else vertical_labels.get(k, k),
    )
    st.session_state["knowledge_filter"] = selection

    st.session_state["knowledge_show_advanced"] = c3.toggle(
        "Mostrar opciones avanzadas",
        value=bool(st.session_state.get("knowledge_show_advanced")),
    )

    with st.expander("Guía rápida", expanded=False):
        st.markdown(
            """
- Crea una **Plantilla principal** (Vertical)
- Añade **Especialidades** (Scopes)
- Define **Guiones** (Flows)
- Añade **Problemas frecuentes** (Subflows)
            """
        )


# -----------------------------------------------------------------------------
# Wizard
# -----------------------------------------------------------------------------


def _wizard_init():
    st.session_state.setdefault("knowledge_wizard", {})
    wiz = st.session_state["knowledge_wizard"]
    wiz.setdefault("step", 1)
    wiz.setdefault("basic", {"key": "", "label": "", "description": "", "default_flow_id": ""})
    wiz.setdefault("scopes", [])
    wiz.setdefault("subflows", [])
    wiz.setdefault("advanced", {"flow_base": None, "prompt_vertical": "", "prompt_extension": ""})
    return wiz


def _wizard_reset():
    st.session_state["knowledge_wizard"] = {
        "step": 1,
        "basic": {"key": "", "label": "", "description": "", "default_flow_id": ""},
        "scopes": [],
        "subflows": [],
        "advanced": {"flow_base": None, "prompt_vertical": "", "prompt_extension": ""},
    }


def _wizard_add_scope(wiz: dict[str, Any], key: str, label: str):
    k = (key or "").strip().lower()
    if not k:
        st.error("Falta el key de la especialidad.")
        return
    if not _KEY_RE.match(k):
        st.error("Key inválido. Usa minúsculas, números, _ o -.")
        return
    existing = [s["key"] for s in wiz.get("scopes", [])]
    if k in existing:
        st.warning("Esa especialidad ya está en la lista.")
        return
    wiz.setdefault("scopes", []).append(
        {
            "key": k,
            "label": (label or "").strip() or k,
            "identity": "",
            "goals": [],
            "steps": [],
            "rules": [],
        }
    )


def _wizard_add_subflow(wiz: dict[str, Any], scope: str, save_to: str, key: str, label: str, template_key: str):
    scope_key = (scope or "").strip().lower() or "default"
    save_to = (save_to or "").strip().lower() or "problema"
    sub_key = _slugify_subflow_key(key)
    if not sub_key:
        st.error("Falta key del problema.")
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
    st.caption("Un flujo guiado para crear una plantilla con especialidades y guiones.")

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
            if st.session_state.get("knowledge_show_advanced"):
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
                    "Identidad del experto (opcional)",
                    value=wiz["advanced"].get("prompt_vertical", ""),
                    height=80,
                )
                wiz["advanced"]["prompt_extension"] = st.text_area(
                    "Objetivo (opcional)",
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
        st.markdown("**Especialidades (Scopes)**")
        st.caption("Define 1 o más especialidades donde se usará el guion.")

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
                with st.expander(f"Configurar {s['label']}", expanded=False):
                    ident_val = st.text_area(
                        "Identidad del experto",
                        value=str(s.get("identity") or ""),
                        height=80,
                        key=f"wiz-scope-ident-{idx}",
                    )
                    goals_val = st.text_area(
                        "Objetivos (1 por línea)",
                        value="\n".join(s.get("goals") or []),
                        height=80,
                        key=f"wiz-scope-goals-{idx}",
                    )
                    steps_val = st.text_area(
                        "Guion base (pasos, 1 por línea)",
                        value="\n".join(s.get("steps") or []),
                        height=120,
                        key=f"wiz-scope-steps-{idx}",
                    )
                    rules_val = st.text_area(
                        "Reglas rápidas (1 por línea)",
                        value="\n".join(s.get("rules") or []),
                        height=80,
                        key=f"wiz-scope-rules-{idx}",
                    )
                    s["identity"] = ident_val
                    s["goals"] = [line.strip() for line in goals_val.splitlines() if line.strip()]
                    s["steps"] = [line.strip() for line in steps_val.splitlines() if line.strip()]
                    s["rules"] = [line.strip() for line in rules_val.splitlines() if line.strip()]
        else:
            st.info("Aún no añadiste especialidades. Puedes avanzar si no aplica.")

        c_prev, c_next = st.columns([0.5, 0.5])
        if c_prev.button("Atrás", use_container_width=True):
            wiz["step"] = 1
            st.rerun()
        if c_next.button("Siguiente", use_container_width=True):
            wiz["step"] = 3
            st.rerun()

    elif step == 3:
        st.markdown("**Guiones y problemas frecuentes**")
        st.caption("Define problemas frecuentes (subguiones) por especialidad.")

        scopes = wiz.get("scopes", [])
        scope_options = [s["key"] for s in scopes] or ["default"]
        c1, c2, c3, c4 = st.columns([0.25, 0.2, 0.2, 0.35])
        sf_scope = c1.selectbox("Especialidad", options=scope_options, key="wiz-sf-scope")
        sf_save_to = c2.text_input("save_to", value="problema", key="wiz-sf-save")
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
        if st.button("Agregar problema", use_container_width=True):
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
            st.info("No añadiste problemas (opcional).")

        c_prev, c_save = st.columns([0.5, 0.5])
        if c_prev.button("Atrás", use_container_width=True):
            wiz["step"] = 2
            st.rerun()
        if c_save.button("Crear plantilla", use_container_width=True, disabled=not write_enabled):
            basic = wiz.get("basic", {})
            base_flow = wiz.get("advanced", {}).get("flow_base")
            if not isinstance(base_flow, dict):
                base_flow = _minimal_flow_router(
                    version=(basic.get("default_flow_id") or f"{(basic.get('key') or '').strip()}_base_v1").strip()
                )
            payload = {
                "key": (basic.get("key") or "").strip(),
                "label": (basic.get("label") or "").strip() or None,
                "default_flow_id": (basic.get("default_flow_id") or "").strip() or None,
                "flow_base": base_flow,
            }
            payload = {k: v for k, v in payload.items() if v not in (None, "")}
            with st.spinner("Creando plantilla..."):
                res = create_vertical_admin(ctx.token, payload, api_key=ctx.api_key)
            if isinstance(res, dict) and res.get("error"):
                _show_api_error(res, "No se pudo crear la plantilla")
                return

            vkey = payload["key"].lower()
            created_files: list[str] = ["metadata.json", "flow_base.json"]

            def _write_file(filename: str, *, kind: str, content: Any, validate: bool = True) -> bool:
                out = update_vertical_file_admin(
                    ctx.token,
                    vkey,
                    filename,
                    kind=kind,
                    content=content,
                    validate=validate,
                    api_key=ctx.api_key,
                )
                if isinstance(out, dict) and out.get("error"):
                    _show_api_error(out, f"No se pudo guardar {filename}")
                    return False
                created_files.append(filename)
                return True

            meta_payload = read_vertical_file_admin(ctx.token, vkey, "metadata.json", api_key=ctx.api_key)
            meta_content = meta_payload.get("content") if isinstance(meta_payload, dict) and isinstance(meta_payload.get("content"), dict) else {}
            meta_content.setdefault("archived", False)
            if basic.get("description"):
                meta_content["description"] = basic.get("description")
            if scopes:
                defs = meta_content.get("scope_definitions") if isinstance(meta_content.get("scope_definitions"), dict) else {}
                for s in scopes:
                    scope_key = s["key"]
                    problem_groups = sorted({sf.get("save_to") for sf in wiz.get("subflows", []) if sf.get("scope") == scope_key})
                    goals_list = [line.strip() for line in (s.get("goals") or []) if line.strip()]
                    rules_list = [line.strip() for line in (s.get("rules") or []) if line.strip()]
                    defs[scope_key] = {
                        "label": s.get("label") or scope_key,
                        "flow_id": None,
                        "problem_groups": problem_groups,
                        "goals": goals_list,
                        "objective": "\n".join(goals_list),
                        "rules_toggles": rules_list,
                        "rules_quick": "\n".join(rules_list),
                    }
                meta_content["scope_definitions"] = defs
                scope_cfg = meta_content.get("scope") if isinstance(meta_content.get("scope"), dict) else {}
                included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else []
                for s in scopes:
                    if s["key"] not in included:
                        included.append(s["key"])
                scope_cfg["included"] = included
                meta_content["scope"] = scope_cfg
                if not _write_metadata(vkey, meta_content):
                    for fname in reversed(created_files):
                        delete_vertical_file_admin(ctx.token, vkey, fname, api_key=ctx.api_key)
                    return

            if wiz.get("advanced", {}).get("prompt_vertical"):
                if not _write_file(
                    "prompt_vertical.txt",
                    kind="text",
                    content=wiz.get("advanced", {}).get("prompt_vertical") or "",
                    validate=False,
                ):
                    for fname in reversed(created_files):
                        delete_vertical_file_admin(ctx.token, vkey, fname, api_key=ctx.api_key)
                    return
            if wiz.get("advanced", {}).get("prompt_extension"):
                if not _write_file(
                    "prompt_vertical_extension.txt",
                    kind="text",
                    content=wiz.get("advanced", {}).get("prompt_extension") or "",
                    validate=False,
                ):
                    for fname in reversed(created_files):
                        delete_vertical_file_admin(ctx.token, vkey, fname, api_key=ctx.api_key)
                    return

            for s in scopes:
                sk = s["key"]
                stub = s.get("identity") or (
                    f"Especialidad: {sk}\n"
                    "Objetivo: describe la especialidad del negocio para este scope.\n"
                    "Incluye: servicios, precios, horarios, materiales y políticas cuando aparezcan en los documentos.\n"
                    "Estilo: claro, directo, orientado a captación y agenda.\n"
                )
                if not _write_file(
                    f"prompt_scope_{sk}.txt",
                    kind="text",
                    content=stub,
                    validate=False,
                ):
                    for fname in reversed(created_files):
                        delete_vertical_file_admin(ctx.token, vkey, fname, api_key=ctx.api_key)
                    return

                steps = s.get("steps") or []
                flow_version = f"{vkey}__{sk}__v1"
                if steps:
                    flow_payload = _build_linear_flow(steps=steps, version=flow_version, languages=["es"])
                else:
                    base_tpl = res.get("assets", {}).get("flow_base") if isinstance(res, dict) else None
                    flow_payload = dict(base_tpl) if isinstance(base_tpl, dict) else {}
                    if isinstance(flow_payload, dict) and flow_payload:
                        flow_payload["version"] = flow_version
                    else:
                        flow_payload = _build_linear_flow(steps=[], version=flow_version, languages=["es"])
                if not _write_file(
                    f"flow_base_scope_{sk}.json",
                    kind="json",
                    content=flow_payload,
                    validate=True,
                ):
                    for fname in reversed(created_files):
                        delete_vertical_file_admin(ctx.token, vkey, fname, api_key=ctx.api_key)
                    return

                scope_defs = meta_content.get("scope_definitions") if isinstance(meta_content.get("scope_definitions"), dict) else {}
                if sk in scope_defs:
                    scope_defs[sk]["flow_id"] = flow_version
                    meta_content["scope_definitions"] = scope_defs
                    _write_metadata(vkey, meta_content)

            for sf in wiz.get("subflows", []):
                scope_key = sf.get("scope") or "default"
                save_to = sf.get("save_to") or "problema"
                sub_key = sf.get("key") or "general"
                sf_file = _subflow_filename(scope_key, save_to, sub_key)
                sf_flow = _subflow_skeleton(
                    vertical_key=vkey,
                    scope_key=scope_key,
                    save_to=save_to,
                    subflow_key=sub_key,
                    label=sf.get("label"),
                    template_flow=base_flow,
                    problem={
                        "group": save_to,
                        "title": str(sf.get("label") or sub_key),
                        "symptoms": [],
                        "key_questions": [],
                        "base_answer": "",
                        "fields_to_capture": [],
                        "cta": "",
                    },
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
                if not _write_file(sf_file, kind="json", content=sf_flow, validate=True):
                    for fname in reversed(created_files):
                        delete_vertical_file_admin(ctx.token, vkey, fname, api_key=ctx.api_key)
                    return

            st.success("Plantilla creada.")
            st.session_state.pop("_admin_vertical_catalog", None)
            st.session_state["knowledge_selection"] = {"type": "vertical", "vertical": vkey}
            st.session_state["knowledge_show_wizard"] = False
            _wizard_reset()
            st.rerun()


# -----------------------------------------------------------------------------
# Tree panel
# -----------------------------------------------------------------------------


def _set_selection(payload: dict[str, Any]):
    st.session_state["knowledge_selection"] = payload


def _vertical_tree_item(vertical: dict[str, Any], vertical_label: str, files_index: dict[str, list[dict[str, Any]]]):
    vkey = str(vertical.get("key") or "")
    scope_items = vertical.get("scope_items") if isinstance(vertical.get("scope_items"), list) else []

    archived = bool(vertical.get("archived"))
    title = f"{vertical_label} · Archivada" if archived else f"{vertical_label}"

    with st.expander(title, expanded=False):
        if st.button("Ver plantilla", key=f"sel-vertical-{vkey}"):
            _set_selection({"type": "vertical", "vertical": vkey})

        for scope in scope_items:
            skey = str(scope.get("key") or "")
            slabel = str(scope.get("label") or skey)
            if st.button(f"Especialidad: {slabel}", key=f"sel-scope-{vkey}-{skey}"):
                _set_selection({"type": "scope", "vertical": vkey, "scope": skey})

            if st.button(f"Guion: {slabel}", key=f"sel-flow-{vkey}-{skey}"):
                _set_selection({"type": "flow", "vertical": vkey, "scope": skey})

            sf_items = files_index.get(skey, [])
            for sf in sf_items:
                label = sf.get("label") or sf.get("key")
                if st.button(f"Problema: {label}", key=f"sel-subflow-{vkey}-{skey}-{sf.get('key')}"):
                    _set_selection(
                        {
                            "type": "subflow",
                            "vertical": vkey,
                            "scope": skey,
                            "save_to": sf.get("save_to"),
                            "subflow_key": sf.get("key"),
                            "file": sf.get("file"),
                        }
                    )


def render_tree_panel(items: list[dict[str, Any]], vertical_labels: dict[str, str]):
    st.markdown("### Navegación")
    if st.button("+ Nuevo vertical", use_container_width=True, disabled=not write_enabled):
        st.session_state["knowledge_show_wizard"] = True

    if not items:
        st.info("No se encontraron plantillas.")
        return

    for v in items:
        key = str(v.get("key") or "")
        label = vertical_labels.get(key, key)
        files_payload = list_vertical_files_admin(ctx.token, key, api_key=ctx.api_key)
        files_items = files_payload.get("items") if isinstance(files_payload, dict) else []
        subflow_index: dict[str, list[dict[str, Any]]] = {}
        for it in files_items:
            if not isinstance(it, dict):
                continue
            sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
            if not isinstance(sf, dict):
                continue
            scope = str(sf.get("scope") or "")
            if not scope:
                continue
            subflow_index.setdefault(scope, []).append(
                {
                    "key": _slugify_subflow_key(sf.get("key")),
                    "label": sf.get("label"),
                    "save_to": sf.get("save_to"),
                    "file": it.get("normalized_filename") or it.get("filename"),
                }
            )
        _vertical_tree_item(v, label, subflow_index)


# -----------------------------------------------------------------------------
# Actions (duplicate / delete)
# -----------------------------------------------------------------------------


def _copy_vertical_files(src_key: str, dest_key: str):
    files_payload = list_vertical_files_admin(ctx.token, src_key, api_key=ctx.api_key)
    files_items = files_payload.get("items") if isinstance(files_payload, dict) else []
    for it in files_items:
        fname = str(it.get("normalized_filename") or it.get("filename") or "").strip()
        if not fname:
            continue
        file_data = read_vertical_file_admin(ctx.token, src_key, fname, api_key=ctx.api_key)
        if isinstance(file_data, dict) and file_data.get("error"):
            continue
        content = file_data.get("content") if isinstance(file_data, dict) else None
        kind = (file_data.get("kind") if isinstance(file_data, dict) else "json") or "json"
        if content is None:
            continue
        if fname == "metadata.json":
            continue
        update_vertical_file_admin(
            ctx.token,
            dest_key,
            fname,
            kind=str(kind),
            content=content,
            validate=False,
            api_key=ctx.api_key,
        )


def _duplicate_vertical(detail: dict[str, Any], *, new_key: str, new_label: str | None):
    src_key = detail.get("key")
    cfg = detail.get("config") if isinstance(detail.get("config"), dict) else {}
    assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
    flow_base = assets.get("flow_base") if isinstance(assets.get("flow_base"), dict) else None
    payload = {
        "key": new_key,
        "label": (new_label or "").strip() or f"{cfg.get('label') or src_key} (Copia)",
        "default_flow_id": cfg.get("default_flow_id"),
        "flow_base": flow_base,
    }
    res = create_vertical_admin(ctx.token, payload, api_key=ctx.api_key)
    if isinstance(res, dict) and res.get("error"):
        _show_api_error(res, "No se pudo duplicar la plantilla")
        return
    meta_src = assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {}
    if meta_src:
        meta_copy = dict(meta_src)
        meta_copy["vertical_key"] = new_key
        meta_copy["label"] = payload["label"]
        update_vertical_file_admin(
            ctx.token,
            new_key,
            "metadata.json",
            kind="json",
            content=meta_copy,
            validate=True,
            api_key=ctx.api_key,
        )
    _copy_vertical_files(src_key, new_key)
    st.success("Plantilla duplicada.")
    st.session_state.pop("_admin_vertical_catalog", None)
    st.session_state["knowledge_selection"] = {"type": "vertical", "vertical": new_key}
    st.rerun()


def _duplicate_scope(vertical_key: str, scope_key: str, *, new_key: str, new_label: str | None):
    detail = _load_vertical_detail(vertical_key)
    if not detail:
        return
    assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
    meta = assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {}
    scope_defs = _resolve_scope_defs(detail)
    if scope_key not in scope_defs:
        st.error("Especialidad no encontrada.")
        return
    if new_key in scope_defs:
        st.error("Ya existe una especialidad con ese key.")
        return
    base_def = scope_defs.get(scope_key)
    scope_defs[new_key] = dict(base_def) if isinstance(base_def, dict) else {"label": new_key}
    scope_defs[new_key]["label"] = (new_label or "").strip() or new_key
    meta["scope_definitions"] = scope_defs
    meta.setdefault("scope", {})
    included = meta["scope"].get("included") if isinstance(meta["scope"].get("included"), list) else []
    if new_key not in included:
        included.append(new_key)
    meta["scope"]["included"] = included
    if not _write_metadata(vertical_key, meta):
        return

    old_prompt = _load_text_file(vertical_key, f"prompt_scope_{scope_key}.txt")
    if old_prompt:
        update_vertical_file_admin(
            ctx.token,
            vertical_key,
            f"prompt_scope_{new_key}.txt",
            kind="text",
            content=old_prompt,
            validate=False,
            api_key=ctx.api_key,
        )

    flow_src = _load_flow(vertical_key, f"flow_base_scope_{scope_key}.json")
    flow_version = f"{vertical_key}__{new_key}__v1"
    if flow_src:
        flow_src = dict(flow_src)
        flow_src["version"] = flow_version
        update_vertical_file_admin(
            ctx.token,
            vertical_key,
            f"flow_base_scope_{new_key}.json",
            kind="json",
            content=flow_src,
            validate=True,
            api_key=ctx.api_key,
        )
        scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
        if new_key in scope_defs:
            scope_defs[new_key]["flow_id"] = flow_version
            meta["scope_definitions"] = scope_defs
            _write_metadata(vertical_key, meta)

    files_payload = list_vertical_files_admin(ctx.token, vertical_key, api_key=ctx.api_key)
    items = files_payload.get("items") if isinstance(files_payload, dict) else []
    for it in items:
        sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
        if isinstance(sf, dict) and str(sf.get("scope")) == str(scope_key):
            save_to = sf.get("save_to")
            key = sf.get("key")
            src_file = it.get("normalized_filename") or it.get("filename")
            if not src_file:
                continue
            data = read_vertical_file_admin(ctx.token, vertical_key, src_file, api_key=ctx.api_key)
            content = data.get("content") if isinstance(data, dict) else None
            if not isinstance(content, dict):
                continue
            cfg = content.get("config") if isinstance(content.get("config"), dict) else {}
            sub_cfg = cfg.get("subflow") if isinstance(cfg.get("subflow"), dict) else {}
            sub_cfg["scope"] = new_key
            cfg["subflow"] = sub_cfg
            content["config"] = cfg
            content["version"] = _subflow_flow_id(
                vertical_key=vertical_key,
                scope_key=new_key,
                save_to=str(save_to),
                subflow_key=str(key),
            )
            dest_file = _subflow_filename(new_key, str(save_to), str(key))
            update_vertical_file_admin(
                ctx.token,
                vertical_key,
                dest_file,
                kind="json",
                content=content,
                validate=True,
                api_key=ctx.api_key,
            )

        routes = it.get("router_routes") if isinstance(it.get("router_routes"), dict) else None
        if isinstance(routes, dict) and str(routes.get("scope")) == str(scope_key):
            save_to = routes.get("save_to")
            src_file = it.get("normalized_filename") or it.get("filename")
            data = read_vertical_file_admin(ctx.token, vertical_key, src_file, api_key=ctx.api_key)
            content = data.get("content") if isinstance(data, dict) else None
            if not isinstance(content, dict):
                continue
            new_routes = {}
            for opt, entry in (content.get("routes") or {}).items():
                if not isinstance(entry, dict):
                    continue
                sf_id = entry.get("subflow_id")
                sf_file = entry.get("file")
                if sf_id:
                    parts = str(sf_id).split("__")
                    if len(parts) >= 4:
                        parts[1] = new_key
                        sf_id = "__".join(parts)
                if sf_file:
                    try:
                        sf_key = sf_file.split("__")[-1].replace(".json", "")
                        sf_file = _subflow_filename(new_key, str(save_to), sf_key)
                    except Exception:
                        pass
                new_routes[opt] = {"subflow_id": sf_id, "file": sf_file}
            content["routes"] = new_routes
            dest_file = _routes_filename(new_key, str(save_to))
            update_vertical_file_admin(
                ctx.token,
                vertical_key,
                dest_file,
                kind="json",
                content=content,
                validate=False,
                api_key=ctx.api_key,
            )

    st.success("Especialidad duplicada.")
    st.session_state["knowledge_selection"] = {"type": "scope", "vertical": vertical_key, "scope": new_key}
    st.rerun()


def _delete_scope(vertical_key: str, scope_key: str, meta: dict[str, Any]):
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    scope_defs.pop(scope_key, None)
    meta["scope_definitions"] = scope_defs
    scope_cfg = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
    included = scope_cfg.get("included") if isinstance(scope_cfg.get("included"), list) else []
    scope_cfg["included"] = [k for k in included if k != scope_key]
    meta["scope"] = scope_cfg
    if not _write_metadata(vertical_key, meta):
        return

    for fname in [f"prompt_scope_{scope_key}.txt", f"flow_base_scope_{scope_key}.json"]:
        try:
            delete_vertical_file_admin(ctx.token, vertical_key, fname, api_key=ctx.api_key)
        except Exception:
            pass

    files_payload = list_vertical_files_admin(ctx.token, vertical_key, api_key=ctx.api_key)
    items = files_payload.get("items") if isinstance(files_payload, dict) else []
    for it in items:
        sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
        if isinstance(sf, dict) and str(sf.get("scope")) == str(scope_key):
            fname = it.get("normalized_filename") or it.get("filename")
            if fname:
                delete_vertical_file_admin(ctx.token, vertical_key, fname, api_key=ctx.api_key)
        rr = it.get("router_routes") if isinstance(it.get("router_routes"), dict) else None
        if isinstance(rr, dict) and str(rr.get("scope")) == str(scope_key):
            fname = it.get("normalized_filename") or it.get("filename")
            if fname:
                delete_vertical_file_admin(ctx.token, vertical_key, fname, api_key=ctx.api_key)

    st.success("Especialidad eliminada.")
    st.session_state["knowledge_selection"] = {"type": "vertical", "vertical": vertical_key}
    st.rerun()


def _archive_vertical(vertical_key: str, archived: bool):
    detail = _load_vertical_detail(vertical_key)
    if not detail:
        return
    assets = detail.get("assets") if isinstance(detail.get("assets"), dict) else {}
    meta = assets.get("metadata") if isinstance(assets.get("metadata"), dict) else {}
    meta["archived"] = bool(archived)
    if _write_metadata(vertical_key, meta):
        st.success("Plantilla archivada." if archived else "Plantilla reactivada.")
        st.session_state.pop("_admin_vertical_catalog", None)
        st.session_state["knowledge_selection"] = {"type": "vertical", "vertical": vertical_key}
        st.rerun()


def _delete_vertical_assets(vertical_key: str):
    files_payload = list_vertical_files_admin(ctx.token, vertical_key, api_key=ctx.api_key)
    items = files_payload.get("items") if isinstance(files_payload, dict) else []
    for it in items:
        fname = it.get("normalized_filename") or it.get("filename")
        if fname:
            try:
                delete_vertical_file_admin(ctx.token, vertical_key, fname, api_key=ctx.api_key)
            except Exception:
                continue
    st.warning("Se eliminaron archivos editables. Los archivos base (metadata/flow_base) requieren borrado manual si aplica.")


# -----------------------------------------------------------------------------
# Editor panel
# -----------------------------------------------------------------------------


def _load_text_file(vertical_key: str, filename: str) -> str:
    resp = read_vertical_file_admin(ctx.token, vertical_key, filename, api_key=ctx.api_key)
    if isinstance(resp, dict) and isinstance(resp.get("content"), str):
        return resp.get("content") or ""
    return ""


def _load_flow(vertical_key: str, filename: str) -> dict[str, Any]:
    resp = read_vertical_file_admin(ctx.token, vertical_key, filename, api_key=ctx.api_key)
    if isinstance(resp, dict) and isinstance(resp.get("content"), dict):
        return resp.get("content") or {}
    return {}


def _save_flow(vertical_key: str, filename: str, flow: dict[str, Any]):
    out = update_vertical_file_admin(
        ctx.token,
        vertical_key,
        filename,
        kind="json",
        content=flow,
        validate=True,
        api_key=ctx.api_key,
    )
    if isinstance(out, dict) and out.get("error"):
        _show_api_error(out, f"No se pudo guardar {filename}")
        return False
    return True


def _extract_linear_steps(flow: dict[str, Any]) -> list[str]:
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    start = flow.get("start_block") if isinstance(flow.get("start_block"), str) else None
    if not start or start not in blocks:
        return list(blocks.keys())
    order = []
    seen = set()
    current = start
    while current and current in blocks and current not in seen:
        order.append(current)
        seen.add(current)
        block = blocks.get(current) or {}
        nxt = block.get("next")
        if not isinstance(nxt, str):
            break
        current = nxt
    return order


def _update_block_text(block: dict[str, Any], text: str):
    if not block:
        return
    if isinstance(block.get("text"), dict):
        block["text"]["es"] = text
    else:
        block["text"] = text


def _update_options_labels(block: dict[str, Any], labels: list[str]):
    options = block.get("options") if isinstance(block.get("options"), list) else None
    if not options:
        return
    for idx, opt in enumerate(options):
        if idx >= len(labels):
            break
        label = labels[idx]
        if isinstance(opt, dict):
            if isinstance(opt.get("label"), dict):
                opt["label"]["es"] = label
            else:
                opt["label"] = label


def _render_flow_editor(vertical_key: str, scope_key: str | None, flow_file: str, meta: dict[str, Any]):
    flow = _load_flow(vertical_key, flow_file)
    if not flow:
        st.warning("No se pudo cargar el guion.")
        return

    st.markdown("#### Identidad del experto")
    if scope_key:
        prompt_file = f"prompt_scope_{scope_key}.txt"
        prompt_value = _load_text_file(vertical_key, prompt_file)
    else:
        prompt_file = "prompt_vertical.txt"
        prompt_value = _load_text_file(vertical_key, prompt_file)
    ident_text = st.text_area("", value=prompt_value, height=120, key=f"ident-{vertical_key}-{scope_key}-{flow_file}")

    st.markdown("#### Objetivo")
    goals_key = "goals"
    scope_defs = meta.get("scope_definitions") if isinstance(meta.get("scope_definitions"), dict) else {}
    if scope_key and scope_key in scope_defs:
        raw_goals = scope_defs.get(scope_key, {}).get(goals_key)
        if not isinstance(raw_goals, list):
            raw_goals = (scope_defs.get(scope_key, {}).get("objective") or "").splitlines()
    else:
        raw_goals = meta.get(goals_key)
        if not isinstance(raw_goals, list):
            raw_goals = (meta.get("objective") or "").splitlines()
    goal_lines = [str(g).strip() for g in (raw_goals or []) if str(g).strip()]
    objective_text = st.text_area(
        "",
        value="\n".join(goal_lines),
        height=80,
        key=f"obj-{vertical_key}-{scope_key}-{flow_file}",
    )

    st.markdown("#### Guion base (pasos)")
    blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}
    step_order = _extract_linear_steps(flow)
    edits: dict[str, dict[str, Any]] = {}
    for bid in step_order:
        block = blocks.get(bid)
        if not isinstance(block, dict):
            continue
        st.markdown(f"**{bid}** · {block.get('type')}")
        text_val = block.get("text")
        if isinstance(text_val, dict):
            text_val = text_val.get("es") or ""
        text_input = st.text_input("Texto", value=str(text_val or ""), key=f"flow-text-{flow_file}-{bid}")
        edits[bid] = {"text": text_input}
        options = block.get("options") if isinstance(block.get("options"), list) else []
        if options:
            opt_labels = []
            for idx, opt in enumerate(options):
                label = opt.get("label") if isinstance(opt, dict) else str(opt)
                if isinstance(label, dict):
                    label = label.get("es") or ""
                opt_labels.append(label)
            new_labels = []
            for idx, label in enumerate(opt_labels):
                new_labels.append(st.text_input("Opción", value=str(label or ""), key=f"flow-opt-{flow_file}-{bid}-{idx}"))
            edits[bid]["options"] = new_labels
        st.divider()

    st.markdown("#### Reglas rápidas")
    rules_key = "rules_toggles"
    if scope_key and scope_key in scope_defs:
        raw_rules = scope_defs.get(scope_key, {}).get(rules_key)
        if not isinstance(raw_rules, list):
            raw_rules = (scope_defs.get(scope_key, {}).get("rules_quick") or "").splitlines()
    else:
        raw_rules = meta.get(rules_key)
        if not isinstance(raw_rules, list):
            raw_rules = (meta.get("rules_quick") or "").splitlines()
    rule_lines = [str(r).strip() for r in (raw_rules or []) if str(r).strip()]
    rules_text = st.text_area(
        "",
        value="\n".join(rule_lines),
        height=80,
        key=f"rules-{vertical_key}-{scope_key}-{flow_file}",
    )

    c1, c2 = st.columns([0.5, 0.5])
    if c1.button("Guardar guion", use_container_width=True, disabled=not write_enabled):
        for bid, data in edits.items():
            block = blocks.get(bid) if isinstance(blocks.get(bid), dict) else None
            if not block:
                continue
            _update_block_text(block, data.get("text", ""))
            if "options" in data:
                _update_options_labels(block, data.get("options") or [])
        flow["blocks"] = blocks
        issues = validate_flow(flow)
        if not _render_validation_issues(issues, title="Guion"):
            return
        if _save_flow(vertical_key, flow_file, flow):
            update_vertical_file_admin(
                ctx.token,
                vertical_key,
                prompt_file,
                kind="text",
                content=ident_text,
                validate=False,
                api_key=ctx.api_key,
            )
            goals_list = [line.strip() for line in objective_text.splitlines() if line.strip()]
            rules_list = [line.strip() for line in rules_text.splitlines() if line.strip()]
            if scope_key and scope_key in scope_defs:
                scope_defs[scope_key][goals_key] = goals_list
                scope_defs[scope_key]["objective"] = "\n".join(goals_list)
                scope_defs[scope_key][rules_key] = rules_list
                scope_defs[scope_key]["rules_quick"] = "\n".join(rules_list)
                meta["scope_definitions"] = scope_defs
            else:
                meta[goals_key] = goals_list
                meta["objective"] = "\n".join(goals_list)
                meta[rules_key] = rules_list
                meta["rules_quick"] = "\n".join(rules_list)
            _write_metadata(vertical_key, meta)
            st.success("Guion actualizado.")
            st.rerun()

    if c2.button("Simulador", use_container_width=True):
        st.session_state["sim_flow"] = {"vertical": vertical_key, "file": flow_file, "block": flow.get("start_block")}

    sim = st.session_state.get("sim_flow")
    if sim and sim.get("file") == flow_file:
        st.markdown("#### Simulador de conversación")
        current_id = sim.get("block")
        block = blocks.get(current_id) if isinstance(blocks.get(current_id), dict) else None
        if not block:
            st.info("Fin del guion.")
        else:
            text_val = block.get("text")
            if isinstance(text_val, dict):
                text_val = text_val.get("es") or ""
            st.write(text_val or "")
            btype = str(block.get("type") or "message")
            if btype in {"buttons", "options"}:
                opts = block.get("options") if isinstance(block.get("options"), list) else []
                opt_labels = []
                opt_values = []
                for opt in opts:
                    if isinstance(opt, dict):
                        label = opt.get("label")
                        if isinstance(label, dict):
                            label = label.get("es") or ""
                        opt_labels.append(str(label or opt.get("value") or ""))
                        opt_values.append(str(opt.get("value") or opt.get("id") or label))
                    else:
                        opt_labels.append(str(opt))
                        opt_values.append(str(opt))
                chosen = st.radio("Opciones", options=list(range(len(opt_labels))), format_func=lambda i: opt_labels[i])
                if st.button("Enviar", key=f"sim-btn-{flow_file}-{current_id}"):
                    next_map = block.get("next_map") if isinstance(block.get("next_map"), dict) else {}
                    next_id = next_map.get(opt_values[chosen]) or block.get("next")
                    st.session_state["sim_flow"]["block"] = next_id
                    st.rerun()
            elif btype in {"input", "text"}:
                st.text_input("Respuesta", key=f"sim-input-{flow_file}-{current_id}")
                if st.button("Enviar", key=f"sim-input-send-{flow_file}-{current_id}"):
                    st.session_state["sim_flow"]["block"] = block.get("next")
                    st.rerun()
            else:
                if st.button("Continuar", key=f"sim-next-{flow_file}-{current_id}"):
                    st.session_state["sim_flow"]["block"] = block.get("next")
                    st.rerun()
        if st.button("Reiniciar", key=f"sim-reset-{flow_file}"):
            st.session_state["sim_flow"]["block"] = flow.get("start_block")
            st.rerun()

    if st.session_state.get("knowledge_show_advanced"):
        with st.expander("Avanzado: JSON completo", expanded=False):
            _json_editor(
                vertical_key=vertical_key,
                title=flow_file,
                filename=flow_file,
                value=flow,
                template=flow,
            )


# -----------------------------------------------------------------------------
# Problems panel
# -----------------------------------------------------------------------------


def _load_subflows(vertical_key: str, scope_key: str, save_to: str | None = None) -> list[dict[str, Any]]:
    files_payload = list_vertical_files_admin(ctx.token, vertical_key, api_key=ctx.api_key)
    items = files_payload.get("items") if isinstance(files_payload, dict) else []
    results = []
    for it in items:
        sf = it.get("subflow") if isinstance(it.get("subflow"), dict) else None
        if not isinstance(sf, dict):
            continue
        if str(sf.get("scope")) != str(scope_key):
            continue
        if save_to and str(sf.get("save_to")) != str(save_to):
            continue
        results.append(
            {
                "key": _slugify_subflow_key(sf.get("key")),
                "label": sf.get("label") or sf.get("key"),
                "save_to": sf.get("save_to"),
                "file": it.get("normalized_filename") or it.get("filename"),
            }
        )
    return results


def render_problems_panel(vertical_key: str, scope_key: str | None):
    st.markdown("### Problemas frecuentes")
    if not scope_key:
        st.info("Selecciona una especialidad para ver sus problemas.")
        return

    save_to = st.text_input("Agrupar por (save_to)", value="problema", key=f"sf-save-to-{vertical_key}-{scope_key}")
    subflows = _load_subflows(vertical_key, scope_key, save_to=save_to)

    c1, c2 = st.columns([0.6, 0.4])
    new_key = c1.text_input("Nuevo problema (key)", value="", key=f"sf-new-key-{vertical_key}-{scope_key}")
    new_label = c2.text_input("Nombre visible", value="", key=f"sf-new-label-{vertical_key}-{scope_key}")
    if st.button("+ Nuevo problema", use_container_width=True, disabled=not write_enabled):
        sub_key = _slugify_subflow_key(new_key)
        if not sub_key:
            st.error("Falta key del problema.")
        else:
            problem = {
                "group": str(save_to),
                "title": str(new_label or sub_key),
                "symptoms": [],
                "key_questions": [],
                "base_answer": "",
                "fields_to_capture": [],
                "cta": "",
            }
            sf_flow = _subflow_skeleton(
                vertical_key=vertical_key,
                scope_key=scope_key,
                save_to=save_to,
                subflow_key=sub_key,
                label=new_label or sub_key,
                template_flow=None,
                problem=problem,
            )
            sf_file = _subflow_filename(scope_key, save_to, sub_key)
            out_sf = update_vertical_file_admin(
                ctx.token,
                vertical_key,
                sf_file,
                kind="json",
                content=sf_flow,
                validate=True,
                api_key=ctx.api_key,
            )
            if isinstance(out_sf, dict) and out_sf.get("error"):
                _show_api_error(out_sf, f"No se pudo crear {sf_file}")
            else:
                st.success("Problema creado.")
                st.rerun()

    if not subflows:
        st.info("No hay problemas para esta especialidad.")
        return

    chosen = st.selectbox(
        "Problema",
        options=subflows,
        format_func=lambda sf: f"{sf.get('label')} ({sf.get('key')})",
        key=f"sf-select-{vertical_key}-{scope_key}",
    )
    sf_file = chosen.get("file") if isinstance(chosen, dict) else None
    if not sf_file:
        return

    sf_data = read_vertical_file_admin(ctx.token, vertical_key, sf_file, api_key=ctx.api_key)
    sf_flow = sf_data.get("content") if isinstance(sf_data, dict) and isinstance(sf_data.get("content"), dict) else {}
    cfg = sf_flow.get("config") if isinstance(sf_flow.get("config"), dict) else {}
    raw_problem = cfg.get("problem") if isinstance(cfg.get("problem"), dict) else {}
    normalized_problem = normalize_problem(
        raw_problem,
        default_group=str(save_to),
        title=str(chosen.get("label") or chosen.get("key") or ""),
    )

    symptoms_text = "\n".join(normalized_problem.get("symptoms") or [])
    questions_text = "\n".join(normalized_problem.get("key_questions") or [])
    response_text = normalized_problem.get("base_answer") or ""
    fields_text = "\n".join(normalized_problem.get("fields_to_capture") or [])
    cta_text = normalized_problem.get("cta") or ""

    st.markdown("#### Sintomatología")
    symptoms_text = st.text_area("", value=symptoms_text, height=80, key=f"sf-symptoms-{sf_file}")
    st.markdown("#### Preguntas clave")
    questions_text = st.text_area("", value=questions_text, height=80, key=f"sf-questions-{sf_file}")
    st.markdown("#### Respuesta base")
    response_text = st.text_area("", value=response_text, height=120, key=f"sf-response-{sf_file}")
    st.markdown("#### Campos a capturar")
    fields_text = st.text_area("", value=fields_text, height=80, key=f"sf-fields-{sf_file}")
    st.markdown("#### CTA")
    cta_text = st.text_area("", value=cta_text, height=80, key=f"sf-cta-{sf_file}")

    c1, c2 = st.columns([0.5, 0.5])
    if c1.button("Guardar problema", use_container_width=True, disabled=not write_enabled):
        cfg = sf_flow.get("config") if isinstance(sf_flow.get("config"), dict) else {}
        problem_payload = {
            "group": str(save_to),
            "title": str(chosen.get("label") or chosen.get("key") or ""),
            "symptoms": [s.strip() for s in symptoms_text.splitlines() if s.strip()],
            "key_questions": [s.strip() for s in questions_text.splitlines() if s.strip()],
            "base_answer": response_text.strip(),
            "fields_to_capture": [s.strip() for s in fields_text.splitlines() if s.strip()],
            "cta": cta_text.strip(),
        }
        if not _render_validation_issues(validate_problem(problem_payload), title="Problema"):
            return
        cfg["problem"] = problem_payload
        sf_flow["config"] = cfg
        out_sf = update_vertical_file_admin(
            ctx.token,
            vertical_key,
            sf_file,
            kind="json",
            content=sf_flow,
            validate=True,
            api_key=ctx.api_key,
        )
        if isinstance(out_sf, dict) and out_sf.get("error"):
            _show_api_error(out_sf, f"No se pudo guardar {sf_file}")
        else:
            st.success("Problema actualizado.")
            st.rerun()

    if c2.button("Eliminar problema", use_container_width=True, disabled=not write_enabled):
        st.session_state["sf_delete_file"] = sf_file

    if st.session_state.get("sf_delete_file") == sf_file:
        confirm = st.text_input("Escribe ELIMINAR para confirmar", key=f"sf-del-confirm-{sf_file}")
        if st.button("Eliminar definitivamente", use_container_width=True, disabled=not write_enabled):
            if confirm.strip().upper() != "ELIMINAR":
                st.error("Confirmación incorrecta.")
            else:
                res_del = delete_vertical_file_admin(ctx.token, vertical_key, sf_file, api_key=ctx.api_key)
                if isinstance(res_del, dict) and res_del.get("error"):
                    _show_api_error(res_del, f"No se pudo borrar {sf_file}")
                else:
                    st.success("Problema eliminado.")
                    st.session_state.pop("sf_delete_file", None)
                    st.rerun()

    if st.session_state.get("knowledge_show_advanced"):
        with st.expander("Avanzado: JSON completo", expanded=False):
            _json_editor(
                vertical_key=vertical_key,
                title=sf_file,
                filename=sf_file,
                value=sf_flow,
                template=None,
            )


# -----------------------------------------------------------------------------
# Main layout
# -----------------------------------------------------------------------------

vertical_items, vertical_keys, vertical_labels = _get_catalog()
show_archived = bool(st.session_state.get("knowledge_show_advanced"))
items = [v for v in vertical_items if show_archived or not v.get("archived")]
render_header(items, vertical_labels)

show_archived = bool(st.session_state.get("knowledge_show_advanced"))
items = [v for v in vertical_items if show_archived or not v.get("archived")]
filter_key = st.session_state.get("knowledge_filter")
if filter_key and filter_key != "Todos":
    items = [v for v in items if str(v.get("key")) == str(filter_key)]
items = _search_filter(items, st.session_state.get("knowledge_search", ""))
selection = _ensure_selection(items)

left, center, right = st.columns([0.25, 0.45, 0.30], gap="large")

with left:
    render_tree_panel(items, vertical_labels)

with center:
    if st.session_state.get("knowledge_show_wizard"):
        render_wizard_create_vertical()
    else:
        sel_vertical = selection.get("vertical")
        sel_scope = selection.get("scope")
        sel_type = selection.get("type")
        if not sel_vertical:
            st.info("Selecciona una plantilla para editar.")
        else:
            detail = _load_vertical_detail(sel_vertical)
            if detail:
                meta = detail.get("assets", {}).get("metadata") if isinstance(detail.get("assets"), dict) else {}
                st.markdown("### Acciones")
                with st.expander("Duplicar o eliminar", expanded=False):
                    st.markdown("**Plantilla principal**")
                    with st.form(f"dup-vertical-{sel_vertical}"):
                        new_key = st.text_input("Nuevo key", value="")
                        new_label = st.text_input("Nuevo nombre visible", value="")
                        submitted = st.form_submit_button("Duplicar plantilla", use_container_width=True, disabled=not write_enabled)
                    if submitted:
                        if not new_key or not _KEY_RE.match(new_key.strip().lower()):
                            st.error("Key inválido para duplicado.")
                        else:
                            _duplicate_vertical(detail, new_key=new_key.strip().lower(), new_label=new_label.strip() or None)

                    meta_archived = False
                    if isinstance(meta, dict):
                        meta_archived = bool(meta.get("archived"))
                    st.markdown("**Archivar plantilla**")
                    st.caption("Archivar oculta la plantilla del árbol y evita usos accidentales.")
                    if meta_archived:
                        if st.button("Reactivar plantilla", use_container_width=True, disabled=not write_enabled):
                            _archive_vertical(sel_vertical, False)
                    else:
                        if st.button("Archivar plantilla", use_container_width=True, disabled=not write_enabled):
                            _archive_vertical(sel_vertical, True)

                    if st.session_state.get("knowledge_show_advanced"):
                        st.divider()
                        st.markdown("**Eliminar definitivo (avanzado)**")
                        st.caption("Esto borra archivos editables. No se puede deshacer.")
                        confirm_hard = st.text_input(
                            "Escribe ELIMINAR para confirmar",
                            key=f"del-vertical-{sel_vertical}",
                        )
                        confirm_check = st.checkbox(
                            "Entiendo que esta acción es permanente",
                            key=f"del-vertical-check-{sel_vertical}",
                        )
                        if st.button("Eliminar definitivamente", use_container_width=True, disabled=not write_enabled):
                            if confirm_hard.strip().upper() != "ELIMINAR" or not confirm_check:
                                st.error("Confirmación incorrecta.")
                            else:
                                _delete_vertical_assets(sel_vertical)

                    if sel_scope:
                        st.divider()
                        st.markdown("**Especialidad**")
                        with st.form(f"dup-scope-{sel_vertical}-{sel_scope}"):
                            new_scope_key = st.text_input("Nuevo key", value="")
                            new_scope_label = st.text_input("Nuevo nombre visible", value="")
                            submitted_scope = st.form_submit_button("Duplicar especialidad", use_container_width=True, disabled=not write_enabled)
                        if submitted_scope:
                            if not new_scope_key or not _KEY_RE.match(new_scope_key.strip().lower()):
                                st.error("Key inválido para duplicado.")
                            else:
                                _duplicate_scope(sel_vertical, sel_scope, new_key=new_scope_key.strip().lower(), new_label=new_scope_label.strip() or None)

                        confirm_scope = st.text_input("Escribe ELIMINAR para borrar la especialidad", key=f"del-scope-{sel_vertical}-{sel_scope}")
                        if st.button("Eliminar especialidad", use_container_width=True, disabled=not write_enabled):
                            if confirm_scope.strip().upper() != "ELIMINAR":
                                st.error("Confirmación incorrecta.")
                            else:
                                _delete_scope(sel_vertical, sel_scope, meta if isinstance(meta, dict) else {})

                scope_defs = _resolve_scope_defs(detail)
                flow_file = "flow_base.json" if not sel_scope else f"flow_base_scope_{sel_scope}.json"
                st.markdown("### Editor de guion")
                st.caption("Campos simplificados para editar el contenido sin tocar JSON.")
                _render_flow_editor(sel_vertical, sel_scope, flow_file, meta if isinstance(meta, dict) else {})

                if st.session_state.get("knowledge_show_advanced"):
                    st.divider()
                    st.markdown("### Test IA (avanzado)")
                    st.caption("Prueba la generación para validar prompts.")
                    test_mode = st.radio(
                        "Modo",
                        options=["Dry-run (preview prompt)", "Real (llama IA)"],
                        horizontal=True,
                        key=f"gen-mode-{sel_vertical}",
                    )
                    scope_keys = sorted(scope_defs.keys())
                    test_scopes = st.multiselect(
                        "Especialidades usadas en el test",
                        options=scope_keys,
                        default=scope_keys,
                        key=f"gen-scopes-{sel_vertical}",
                    )
                    test_langs = st.multiselect(
                        "Idiomas",
                        options=["es", "pt", "en", "ca"],
                        default=["es", "pt", "en", "ca"],
                        key=f"gen-langs-{sel_vertical}",
                    )
                    tenant_name = st.text_input("Nombre de tenant (opcional)", value="", key=f"gen-tenant-name-{sel_vertical}")
                    business_knowledge = st.text_area(
                        "Business knowledge (opcional)",
                        value="",
                        height=120,
                        key=f"gen-kb-{sel_vertical}",
                    )
                    model = None
                    temperature = 0.3
                    if test_mode.startswith("Real"):
                        c1, c2 = st.columns([0.6, 0.4])
                        model = c1.selectbox(
                            "Modelo (opcional)",
                            options=["(default)", "gpt-4o-mini", "gpt-4o"],
                            index=0,
                            key=f"gen-model-{sel_vertical}",
                        )
                        temperature = float(
                            c2.slider(
                                "Temperature",
                                min_value=0.0,
                                max_value=1.0,
                                value=0.3,
                                step=0.05,
                                key=f"gen-temp-{sel_vertical}",
                            )
                        )
                        if model == "(default)":
                            model = None

                    if st.button("Ejecutar test", use_container_width=True, key=f"gen-run-{sel_vertical}"):
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
                            res = preview_vertical_flow_generator(ctx.token, sel_vertical, payload, api_key=ctx.api_key)
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

with right:
    sel_vertical = selection.get("vertical")
    sel_scope = selection.get("scope")
    if sel_vertical:
        render_problems_panel(sel_vertical, sel_scope)
    else:
        st.info("Selecciona una plantilla para ver problemas.")
