from __future__ import annotations

import json
from typing import Any

import streamlit as st

from auth import ensure_login
from nav import render_sidebar, show_flash, nav_v2_enabled
from api_client import (
    get_flow_v2_quota,
    generate_flow_v2,
    get_flow_v2_draft,
    get_flow_v2_published,
    reset_flow_v2_draft_from_runtime,
    patch_flow_v2_block,
    patch_flow_v2_blocks,
    publish_flow_v2,
    list_flow_v2_subflows,
    get_flow_v2_subflow,
    patch_flow_v2_subflow_block,
    update_flow_v2_subflows,
    preview_flow_v2_subflows,
)
from utils import load_styles, empty_state, pill


st.set_page_config(page_title="Flujo", page_icon="🧩", layout="wide")
load_styles()
ensure_login()
if not nav_v2_enabled():
    st.switch_page("pages/05_Flujo.py")
    st.stop()
render_sidebar()
show_flash()

st.title("Flujo (v2)")
st.caption("Estructura fija (scope base) + IA como patch de textos/labels (cuota por plan) + edición manual.")

st.markdown("### Setup rápido")
c1, c2, c3 = st.columns([0.34, 0.33, 0.33])
if c1.button("1) Documentos (KB)", use_container_width=True):
    st.switch_page("pages/documentos.py")
if c2.button("2) Automatización (visual/IA)", use_container_width=True):
    st.switch_page("pages/automatizacion.py")
if c3.button("3) Flujo (esta página)", use_container_width=True, disabled=True):
    pass

st.caption("Flujo recomendado: Documentos → Actualizar textos con IA (opcional) → Editar → Publicar.")


def _safe_dict(x):
    return x if isinstance(x, dict) else {}

def _detail_code(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    detail = payload.get("detail")
    if isinstance(detail, dict):
        inner = detail.get("detail")
        return str(inner or "")
    if isinstance(detail, str):
        return detail
    return ""


quota = _safe_dict(get_flow_v2_quota())
if quota.get("status_code"):
    empty_state("No pudimos cargar cuota", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
else:
    st.markdown(
        f"Cuota mensual de generación IA: **{quota.get('used', 0)} / {quota.get('limit', '—')}** "
        f"(restantes: **{quota.get('remaining', '—')}**)."
    )

st.divider()

st.subheader("Generar flujo por IA")
allow_overage = st.toggle("Permitir overage (cobro extra)", value=False)
langs = st.multiselect("Idiomas del flujo", options=["es", "pt", "en", "ca"], default=["es", "pt", "en", "ca"])

colg1, colg2 = st.columns([0.6, 0.4])
if colg1.button("Actualizar textos con IA (no cambia estructura)", use_container_width=True):
    with st.spinner("Generando…"):
        res = generate_flow_v2(allow_overage=bool(allow_overage), languages=list(langs or []))
    if isinstance(res, dict) and res.get("flow_id"):
        st.success(f"Draft actualizado (v{res.get('version')}).")
        st.rerun()
    code = _detail_code(res) if isinstance(res, dict) else ""
    if code == "ia_disabled_for_tenant":
        st.error("La IA está deshabilitada para este tenant. Actívala en Admin (Tenants → “IA habilitada”).")
        st.info("Mientras tanto, puedes usar “Crear draft desde flow base (sin IA)” y editar manualmente.")
    elif code in {"missing_openai_api_key", "invalid_openai_api_key"}:
        st.error("La IA no está configurada en el backend (OpenAI API key inválida o ausente).")
        st.caption("Solución: actualiza `OPENAI_API_KEY` en `backend/.env` y reinicia el backend.")
    elif code in {"ia_provider_unavailable", "ia_rate_limited"}:
        st.error("El proveedor de IA no está disponible ahora. Intenta de nuevo en unos minutos.")
    else:
        st.error(res)

if colg2.button("Crear draft desde flow base (sin IA)", use_container_width=True):
    with st.spinner("Creando draft…"):
        res = reset_flow_v2_draft_from_runtime()
    if isinstance(res, dict) and res.get("flow_id"):
        st.success(f"Draft listo (v{res.get('version')}).")
        st.rerun()
    st.error(res)

st.divider()

st.subheader("Estado")
published = _safe_dict(get_flow_v2_published())
draft = _safe_dict(get_flow_v2_draft())

pub_meta = published.get("published") if isinstance(published.get("published"), dict) else None
dr_meta = draft.get("draft") if isinstance(draft.get("draft"), dict) else None

pub_pill = pill("Publicado", "success") if pub_meta else pill("Sin publicado", "warning")
dr_pill = pill("Draft listo", "success") if dr_meta else pill("Sin draft", "warning")
st.markdown(f"{pub_pill} {dr_pill}", unsafe_allow_html=True)

if pub_meta:
    st.caption(f"Publicado: v{pub_meta.get('version')} · {pub_meta.get('published_at') or '—'}")
if dr_meta:
    st.caption(f"Draft: v{dr_meta.get('version')} · {dr_meta.get('updated_at') or '—'}")

flow = draft.get("flow") if isinstance(draft.get("flow"), dict) else {}
blocks = flow.get("blocks") if isinstance(flow.get("blocks"), dict) else {}

if not blocks:
    empty_state("Sin draft para editar", "Genera un flujo por IA o crea un draft desde el flujo actual.", icon="🧩")
    st.stop()

languages = flow.get("languages") if isinstance(flow.get("languages"), list) else ["es"]
languages = [str(x) for x in languages if x] or ["es"]

st.divider()
st.subheader("Editor (textos y opciones)")
st.caption("Solo edita textos y opciones. La lógica/ramas se mantiene controlada por el sistema.")

status_ph = st.empty()

col_bulk1, col_bulk2 = st.columns([0.5, 0.5])
save_bulk_text = col_bulk1.button("Guardar todos los textos", use_container_width=True)
save_bulk_opts = col_bulk2.button("Guardar todas las opciones (labels)", use_container_width=True)

col_bulk3, col_bulk4 = st.columns([0.5, 0.5])
save_bulk_all = col_bulk3.button("Guardar todo (textos + opciones)", use_container_width=True)
save_bulk_publish = col_bulk4.button("Guardar todo + Publicar", use_container_width=True)

publish_clicked = st.button("Publicar (siempre guarda antes)", use_container_width=True)


def _get_text(block: dict, lang: str) -> str:
    txt = block.get("text")
    if isinstance(txt, dict):
        return str(txt.get(lang) or "")
    if isinstance(txt, str):
        return txt
    return ""


def _set_text_patch(block_id: str, values_by_lang: dict):
    payload = {"text": values_by_lang}
    return patch_flow_v2_block(block_id, payload)


def _patch_options(block_id: str, options: list[dict]):
    payload = {"options": options}
    return patch_flow_v2_block(block_id, payload)


def _normalize_label(label: Any) -> Any:
    if isinstance(label, dict):
        return {k: str(v) for k, v in label.items() if v is not None}
    if isinstance(label, str):
        return label
    return ""


def _patch_subflow_text(subflow_key: str, block_id: str, values_by_lang: dict[str, str]):
    return patch_flow_v2_subflow_block(subflow_key, block_id, {"text": values_by_lang})


def _patch_subflow_options(subflow_key: str, block_id: str, options: list[dict]):
    return patch_flow_v2_subflow_block(subflow_key, block_id, {"options": options})


def _patch_subflow_text_enriched(subflow_key: str, block_id: str, values_by_lang: dict[str, str]):
    return patch_flow_v2_subflow_block(subflow_key, block_id, {"text_enriched": values_by_lang})


def _patch_subflow_text_variants(subflow_key: str, block_id: str, variants: list[str]):
    return patch_flow_v2_subflow_block(subflow_key, block_id, {"text_variants": variants})


def _compute_dirty_blocks() -> set[str]:
    dirty: set[str] = set()
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        btype = str(block.get("type") or "")

        if "text" in block:
            current_txt = block.get("text")
            for lang in languages:
                key = f"txt-{block_id}-{lang}"
                new_val = st.session_state.get(key, _get_text(block, lang))
                new_val = str(new_val or "")
                old_val = ""
                if isinstance(current_txt, dict):
                    old_val = str(current_txt.get(lang) or "")
                elif isinstance(current_txt, str):
                    old_val = str(current_txt or "")
                if new_val != old_val:
                    dirty.add(block_id)
                    break

        if btype in {"buttons", "options"}:
            existing = block.get("options") if isinstance(block.get("options"), list) else []
            for opt in existing:
                if not isinstance(opt, dict):
                    continue
                oid = str(opt.get("id") or opt.get("value") or "").strip()
                if not oid:
                    continue
                old_label = _normalize_label(opt.get("label"))
                if isinstance(old_label, dict):
                    for lang in languages:
                        key = f"opt-{block_id}-{oid}-{lang}"
                        new_val = st.session_state.get(key, str(old_label.get(lang) or ""))
                        if str(new_val or "") != str(old_label.get(lang) or ""):
                            dirty.add(block_id)
                            break
                    if block_id in dirty:
                        break
                else:
                    key = f"opt-{block_id}-{oid}"
                    new_val = st.session_state.get(key, str(old_label or ""))
                    if str(new_val or "") != str(old_label or ""):
                        dirty.add(block_id)
                        break

            new_opt_id = str(st.session_state.get(f"new-opt-id-{block_id}", "") or "").strip()
            if new_opt_id:
                dirty.add(block_id)

    return dirty


def _bulk_save_texts() -> dict:
    patches: list[dict] = []
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        if "text" not in block:
            continue
        current_txt = block.get("text")
        values_by_lang: dict[str, str] = {}
        changed = False
        for lang in languages:
            key = f"txt-{block_id}-{lang}"
            new_val = st.session_state.get(key, _get_text(block, lang))
            new_val = str(new_val or "")
            values_by_lang[lang] = new_val
            old_val = ""
            if isinstance(current_txt, dict):
                old_val = str(current_txt.get(lang) or "")
            elif isinstance(current_txt, str):
                old_val = str(current_txt or "")
            if new_val != old_val:
                changed = True
        if changed:
            patches.append({"block_id": block_id, "text": values_by_lang})
    if not patches:
        return {"skipped": True, "detail": "no_changes"}
    return patch_flow_v2_blocks({"patches": patches})


def _bulk_save_options() -> dict:
    patches: list[dict] = []
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        btype = str(block.get("type") or "")
        if btype not in {"buttons", "options"}:
            continue
        existing = block.get("options") if isinstance(block.get("options"), list) else []
        has_branching = isinstance(block.get("next_map"), dict) or isinstance(block.get("branches"), dict)
        allow_add = (not has_branching) and bool(block.get("next"))
        opt_patches: list[dict] = []
        changed = False
        for opt in existing or []:
            if not isinstance(opt, dict):
                continue
            oid = str(opt.get("id") or opt.get("value") or "").strip()
            if not oid:
                continue
            old_label = _normalize_label(opt.get("label"))
            if isinstance(old_label, dict):
                new_lbl: dict[str, str] = {}
                for lang in languages:
                    key = f"opt-{block_id}-{oid}-{lang}"
                    new_val = st.session_state.get(key, str(old_label.get(lang) or ""))
                    new_val = str(new_val or "")
                    new_lbl[lang] = new_val
                    if new_val != str(old_label.get(lang) or ""):
                        changed = True
                opt_patches.append({"id": oid, "label": new_lbl})
            else:
                key = f"opt-{block_id}-{oid}"
                new_val = st.session_state.get(key, str(old_label or ""))
                new_val = str(new_val or "")
                if new_val != str(old_label or ""):
                    changed = True
                opt_patches.append({"id": oid, "label": new_val})

        new_id = str(st.session_state.get(f"new-opt-id-{block_id}", "") or "").strip()
        if new_id and allow_add:
            new_labels: dict[str, str] = {}
            for lang in languages:
                key = f"new-opt-label-{block_id}-{lang}"
                new_labels[lang] = str(st.session_state.get(key, "") or "")
            opt_patches.append({"id": new_id, "label": new_labels})
            changed = True
        if changed and opt_patches:
            patches.append({"block_id": block_id, "options": opt_patches})
    if not patches:
        return {"skipped": True, "detail": "no_changes"}
    return patch_flow_v2_blocks({"patches": patches})


def _bulk_save_all() -> dict:
    patches: dict[str, dict] = {}

    # texts
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        if "text" not in block:
            continue
        current_txt = block.get("text")
        values_by_lang: dict[str, str] = {}
        changed = False
        for lang in languages:
            key = f"txt-{block_id}-{lang}"
            new_val = st.session_state.get(key, _get_text(block, lang))
            new_val = str(new_val or "")
            values_by_lang[lang] = new_val
            old_val = ""
            if isinstance(current_txt, dict):
                old_val = str(current_txt.get(lang) or "")
            elif isinstance(current_txt, str):
                old_val = str(current_txt or "")
            if new_val != old_val:
                changed = True
        if changed:
            patches.setdefault(block_id, {})["text"] = values_by_lang

    # options (+ optional new option on non-branching)
    for block_id, block in blocks.items():
        if not isinstance(block, dict):
            continue
        btype = str(block.get("type") or "")
        if btype not in {"buttons", "options"}:
            continue
        existing = block.get("options") if isinstance(block.get("options"), list) else []
        has_branching = isinstance(block.get("next_map"), dict) or isinstance(block.get("branches"), dict)
        allow_add = (not has_branching) and bool(block.get("next"))
        opt_patches: list[dict] = []
        changed = False
        for opt in existing or []:
            if not isinstance(opt, dict):
                continue
            oid = str(opt.get("id") or opt.get("value") or "").strip()
            if not oid:
                continue
            old_label = _normalize_label(opt.get("label"))
            if isinstance(old_label, dict):
                new_lbl: dict[str, str] = {}
                for lang in languages:
                    key = f"opt-{block_id}-{oid}-{lang}"
                    new_val = st.session_state.get(key, str(old_label.get(lang) or ""))
                    new_val = str(new_val or "")
                    new_lbl[lang] = new_val
                    if new_val != str(old_label.get(lang) or ""):
                        changed = True
                opt_patches.append({"id": oid, "label": new_lbl})
            else:
                key = f"opt-{block_id}-{oid}"
                new_val = st.session_state.get(key, str(old_label or ""))
                new_val = str(new_val or "")
                if new_val != str(old_label or ""):
                    changed = True
                opt_patches.append({"id": oid, "label": new_val})

        new_id = str(st.session_state.get(f"new-opt-id-{block_id}", "") or "").strip()
        if new_id and allow_add:
            new_labels: dict[str, str] = {}
            for lang in languages:
                key = f"new-opt-label-{block_id}-{lang}"
                new_labels[lang] = str(st.session_state.get(key, "") or "")
            opt_patches.append({"id": new_id, "label": new_labels})
            changed = True

        if changed and opt_patches:
            patches.setdefault(block_id, {})["options"] = opt_patches

    patch_list = [{"block_id": bid, **data} for bid, data in patches.items() if data]
    if not patch_list:
        return {"skipped": True, "detail": "no_changes"}
    return patch_flow_v2_blocks({"patches": patch_list})


def _bulk_save_and_publish() -> tuple[dict, dict]:
    save_res = _bulk_save_all()
    if isinstance(save_res, dict) and save_res.get("status_code"):
        return save_res, {"skipped": True}
    pub = publish_flow_v2()
    return save_res, pub


if save_bulk_text:
    with st.spinner("Guardando textos…"):
        res = _bulk_save_texts()
    if isinstance(res, dict) and res.get("status_code"):
        st.error(res)
    elif isinstance(res, dict) and res.get("skipped"):
        st.info("No hay cambios de texto para guardar.")
    else:
        st.success("Textos guardados.")
        st.rerun()

if save_bulk_opts:
    with st.spinner("Guardando opciones…"):
        res = _bulk_save_options()
    if isinstance(res, dict) and res.get("status_code"):
        st.error(res)
    elif isinstance(res, dict) and res.get("skipped"):
        st.info("No hay cambios de opciones para guardar.")
    else:
        st.success("Opciones guardadas.")
        st.rerun()

if save_bulk_all:
    with st.spinner("Guardando todo…"):
        res = _bulk_save_all()
    if isinstance(res, dict) and res.get("status_code"):
        st.error(res)
    elif isinstance(res, dict) and res.get("skipped"):
        st.info("No hay cambios para guardar.")
    else:
        st.success("Cambios guardados.")
        st.rerun()

if save_bulk_publish or publish_clicked:
    with st.spinner("Guardando y publicando…"):
        save_res, pub_res = _bulk_save_and_publish()
    if isinstance(save_res, dict) and save_res.get("status_code"):
        st.error(save_res)
    elif isinstance(pub_res, dict) and pub_res.get("status_code"):
        st.error(pub_res)
    elif isinstance(pub_res, dict) and pub_res.get("flow_id"):
        st.success(f"Publicado v{pub_res.get('version')}.")
        st.rerun()
    else:
        st.error(pub_res)

dirty_blocks = _compute_dirty_blocks()
unsavable_new_options: list[str] = []
for block_id, block in blocks.items():
    if not isinstance(block, dict):
        continue
    new_id = str(st.session_state.get(f"new-opt-id-{block_id}", "") or "").strip()
    if not new_id:
        continue
    has_branching = isinstance(block.get("next_map"), dict) or isinstance(block.get("branches"), dict)
    allow_add = (not has_branching) and bool(block.get("next"))
    if not allow_add:
        unsavable_new_options.append(block_id)

with status_ph.container():
    if dirty_blocks:
        st.warning(f"Cambios pendientes en **{len(dirty_blocks)}** bloque(s).")
    else:
        st.info("Sin cambios pendientes.")
    if unsavable_new_options:
        st.caption(
            "Hay nuevas opciones pendientes en bloques con ramas (no se pueden añadir en batch). "
            f"Guárdalas bloque por bloque: {', '.join(unsavable_new_options[:8])}{'…' if len(unsavable_new_options) > 8 else ''}"
        )


block_items = list(blocks.items())
for idx, (block_id, block) in enumerate(block_items, start=1):
    if not isinstance(block, dict):
        continue
    btype = str(block.get("type") or "")
    title = f"{idx}. {block_id} · {btype}"
    preview = _get_text(block, languages[0]).strip().split("\n")[0][:80]
    if preview:
        title = f"{title} — {preview}"

    with st.expander(title, expanded=False):
        # Text editor
        st.markdown("**Texto**")
        cols = st.columns(2)
        edited: dict[str, str] = {}
        for i, lang in enumerate(languages):
            col = cols[i % 2]
            edited[lang] = col.text_area(
                f"Texto ({lang.upper()})",
                value=_get_text(block, lang),
                key=f"txt-{block_id}-{lang}",
                height=110,
            )
        if st.button("Guardar texto", key=f"save-text-{block_id}", use_container_width=True):
            with st.spinner("Guardando…"):
                res = _set_text_patch(block_id, edited)
            if isinstance(res, dict) and res.get("status_code"):
                st.error(res)
            else:
                st.success("Texto guardado.")
                st.rerun()

        # Options editor (if applicable)
        if btype in {"buttons", "options"}:
            st.markdown("**Opciones**")
            existing = block.get("options") if isinstance(block.get("options"), list) else []
            patched: list[dict] = []
            for o in existing:
                if not isinstance(o, dict):
                    continue
                oid = str(o.get("id") or o.get("value") or "").strip()
                if not oid:
                    continue
                label = o.get("label")
                st.markdown(f"- ID: `{oid}`")
                if isinstance(label, dict):
                    lbl_patch = {}
                    for lang in languages:
                        lbl_patch[lang] = st.text_input(
                            f"Label ({lang.upper()}) · {oid}",
                            value=str(label.get(lang) or ""),
                            key=f"opt-{block_id}-{oid}-{lang}",
                        )
                    patched.append({"id": oid, "label": lbl_patch})
                else:
                    val = st.text_input(f"Label · {oid}", value=str(label or ""), key=f"opt-{block_id}-{oid}")
                    patched.append({"id": oid, "label": val})

            st.markdown("**Añadir opción (solo en bloques no-branching)**")
            new_id = st.text_input("ID nueva opción", value="", key=f"new-opt-id-{block_id}")
            if new_id:
                new_labels = {}
                for lang in languages:
                    new_labels[lang] = st.text_input(
                        f"Label ({lang.upper()}) · nueva",
                        value="",
                        key=f"new-opt-label-{block_id}-{lang}",
                    )
                if st.button("Guardar opciones", key=f"save-opts-{block_id}", use_container_width=True):
                    payload_opts = patched + [{"id": new_id.strip(), "label": new_labels}]
                    with st.spinner("Guardando…"):
                        res = _patch_options(block_id, payload_opts)
                    if isinstance(res, dict) and res.get("status_code"):
                        st.error(res)
                    else:
                        st.success("Opciones guardadas.")
                        st.rerun()
            else:
                if st.button("Guardar opciones", key=f"save-opts-{block_id}", use_container_width=True):
                    with st.spinner("Guardando…"):
                        res = _patch_options(block_id, patched)
                    if isinstance(res, dict) and res.get("status_code"):
                        st.error(res)
                    else:
                        st.success("Opciones guardadas.")
                        st.rerun()

        show_debug = st.checkbox("Mostrar JSON (debug)", value=False, key=f"dbg-{block_id}")
        if show_debug:
            st.code(json.dumps(block, ensure_ascii=False, indent=2), language="json")


st.divider()
st.subheader("Sub-flows")
st.caption("Activa/desactiva etapas y personaliza copy sin romper la estructura.")

subflows_payload = _safe_dict(list_flow_v2_subflows())
subflows_list = subflows_payload.get("subflows") if isinstance(subflows_payload.get("subflows"), list) else []
composition_mode = str(subflows_payload.get("composition_mode") or "router").strip().lower()
order_list = subflows_payload.get("order") if isinstance(subflows_payload.get("order"), list) else []
recommended_order = subflows_payload.get("recommended_order") if isinstance(subflows_payload.get("recommended_order"), list) else []

mode_idx = 1 if composition_mode == "sequential" else 0
col_mode1, col_mode2 = st.columns([0.7, 0.3])
mode_choice = col_mode1.selectbox("Modo de composición", options=["router", "sequential"], index=mode_idx, key="sf-mode")
if col_mode2.button("Guardar modo", use_container_width=True):
    res = update_flow_v2_subflows({"composition_mode": mode_choice})
    if isinstance(res, dict) and res.get("status_code"):
        st.error(res)
    else:
        st.success("Modo actualizado.")
        st.rerun()

if not subflows_list:
    st.info("No hay sub-flows detectados para este tenant.")
else:
    all_keys = [str(item.get("key") or "").strip() for item in subflows_list if isinstance(item, dict)]
    all_keys = [k for k in all_keys if k]
    normalized_order = [k for k in order_list if k in all_keys]
    if not normalized_order and recommended_order:
        normalized_order = [k for k in recommended_order if k in all_keys]
    for k in all_keys:
        if k not in normalized_order:
            normalized_order.append(k)

    if "sf_order_list" not in st.session_state or st.session_state.get("sf_order_seed") != ",".join(normalized_order):
        st.session_state["sf_order_list"] = list(normalized_order)
        st.session_state["sf_order_seed"] = ",".join(normalized_order)

    if composition_mode == "sequential":
        st.markdown("**Orden (sequential)**")
        order_state = st.session_state.get("sf_order_list", [])
        sel_key = st.selectbox("Mover sub-flow", options=order_state, index=0, key="sf-order-select")
        c_up, c_down, c_save = st.columns([0.25, 0.25, 0.5])
        if c_up.button("Subir", use_container_width=True):
            idx = order_state.index(sel_key)
            if idx > 0:
                order_state[idx - 1], order_state[idx] = order_state[idx], order_state[idx - 1]
                st.session_state["sf_order_list"] = order_state
                st.rerun()
        if c_down.button("Bajar", use_container_width=True):
            idx = order_state.index(sel_key)
            if idx < len(order_state) - 1:
                order_state[idx + 1], order_state[idx] = order_state[idx], order_state[idx + 1]
                st.session_state["sf_order_list"] = order_state
                st.rerun()
        if c_save.button("Guardar orden", use_container_width=True):
            res = update_flow_v2_subflows({"order": order_state})
            if isinstance(res, dict) and res.get("status_code"):
                st.error(res)
            else:
                st.success("Orden guardado.")
                st.rerun()

        st.markdown("**Activación de sub-flows**")
        enabled_updates: dict[str, bool] = {}
        for item in subflows_list:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key") or "").strip()
            if not key:
                continue
            label = item.get("label")
            label_txt = label.get(languages[0]) if isinstance(label, dict) else (str(label) if label is not None else "")
            title = f"{key} — {label_txt}" if label_txt else key
            required = bool(item.get("required"))
            locked = bool(item.get("locked"))
            enabled_val = bool(item.get("enabled", True))
            col_a, col_b = st.columns([0.75, 0.25])
            col_a.markdown(title + (" 🔒" if locked else "") + (" (obligatorio)" if required else ""))
            enabled_updates[key] = col_b.checkbox(
                "Activo",
                value=True if required else enabled_val,
                disabled=bool(required),
                key=f"sf-enabled-{key}",
            )
        if st.button("Guardar activación", use_container_width=True):
            res = update_flow_v2_subflows({"enabled": enabled_updates})
            if isinstance(res, dict) and res.get("status_code"):
                st.error(res)
            else:
                st.success("Activación guardada.")
                st.rerun()

        if st.button("Generar preview", use_container_width=True):
            preview = _safe_dict(preview_flow_v2_subflows())
            flow_prev = preview.get("flow") if isinstance(preview.get("flow"), dict) else {}
            blocks_prev = flow_prev.get("blocks") if isinstance(flow_prev.get("blocks"), dict) else {}
            st.caption(f"Preview: start=`{flow_prev.get('start_block')}` · blocks={len(blocks_prev)}")
            if blocks_prev:
                st.markdown("**Primeros bloques (preview)**")
                for bid, b in list(blocks_prev.items())[:12]:
                    if not isinstance(b, dict):
                        continue
                    txt = _get_text(b, languages[0]).strip().split("\n")[0][:120]
                    st.write(f"- `{bid}` · {txt}")

    st.markdown("**Editar copy de sub-flow**")
    display_by_key: dict[str, str] = {}
    opt_keys: list[str] = []
    lock_map: dict[str, bool] = {}
    for item in subflows_list:
        if not isinstance(item, dict):
            continue
        k = str(item.get("key") or "").strip()
        if not k:
            continue
        label = item.get("label")
        label_txt = label.get(languages[0]) if isinstance(label, dict) else (str(label) if label is not None else "")
        has_ov = bool(item.get("has_overrides"))
        enabled_val = bool(item.get("enabled", True))
        locked = bool(item.get("locked"))
        lock_map[k] = locked
        title = f"{k} — {label_txt}" if label_txt else k
        if not enabled_val:
            title = f"{title} (desactivado)"
        if has_ov:
            title = f"{title} · personalizado"
        if locked:
            title = f"{title} 🔒"
        display_by_key[k] = title
        opt_keys.append(k)

    selected_key_raw = st.selectbox(
        "Sub-flow",
        options=opt_keys,
        index=0,
        key="sf-select",
        format_func=lambda k: display_by_key.get(str(k), str(k)),
    )

    with st.spinner("Cargando sub-flow…"):
        subflow_info = _safe_dict(get_flow_v2_subflow(selected_key_raw))
    effective_sf = subflow_info.get("effective") if isinstance(subflow_info.get("effective"), dict) else {}
    sf_blocks = effective_sf.get("blocks") if isinstance(effective_sf.get("blocks"), dict) else {}
    sf_langs = effective_sf.get("languages") if isinstance(effective_sf.get("languages"), list) else languages
    sf_langs = [str(x) for x in sf_langs if x] or languages
    is_locked = lock_map.get(selected_key_raw, False)

    if not sf_blocks:
        st.error(subflow_info or "No se pudo cargar el sub-flow.")
    else:
        st.caption(f"Archivo: `{subflow_info.get('file') or '—'}` · blocks: {len(sf_blocks)}")
        if is_locked:
            st.warning("Este sub-flow está bloqueado y no permite edición.")
        for idx2, (sf_block_id, sf_block) in enumerate(list(sf_blocks.items()), start=1):
            if not isinstance(sf_block, dict):
                continue
            sf_type = str(sf_block.get("type") or "")
            title = f"{idx2}. {sf_block_id} · {sf_type}"
            preview = _get_text(sf_block, sf_langs[0]).strip().split("\n")[0][:80]
            if preview:
                title = f"{title} — {preview}"

            with st.expander(title, expanded=False):
                st.markdown("**Texto**")
                cols = st.columns(2)
                edited_sf: dict[str, str] = {}
                for i, lang in enumerate(sf_langs):
                    col = cols[i % 2]
                    edited_sf[lang] = col.text_area(
                        f"Texto ({lang.upper()})",
                        value=_get_text(sf_block, lang),
                        key=f"sf-txt-{selected_key_raw}-{sf_block_id}-{lang}",
                        height=110,
                    )
                if st.button("Guardar texto", key=f"sf-save-text-{selected_key_raw}-{sf_block_id}", use_container_width=True, disabled=is_locked):
                    with st.spinner("Guardando…"):
                        res = _patch_subflow_text(selected_key_raw, sf_block_id, edited_sf)
                    if isinstance(res, dict) and res.get("status_code"):
                        st.error(res)
                    else:
                        st.success("Texto guardado.")
                        st.rerun()

                if isinstance(sf_block.get("text_enriched"), dict):
                    st.markdown("**Texto enriquecido**")
                    cols = st.columns(2)
                    edited_enriched: dict[str, str] = {}
                    for i, lang in enumerate(sf_langs):
                        col = cols[i % 2]
                        edited_enriched[lang] = col.text_area(
                            f"Enriched ({lang.upper()})",
                            value=str(sf_block.get("text_enriched", {}).get(lang) or ""),
                            key=f"sf-enriched-{selected_key_raw}-{sf_block_id}-{lang}",
                            height=110,
                        )
                    if st.button("Guardar enriched", key=f"sf-save-enriched-{selected_key_raw}-{sf_block_id}", use_container_width=True, disabled=is_locked):
                        with st.spinner("Guardando…"):
                            res = _patch_subflow_text_enriched(selected_key_raw, sf_block_id, edited_enriched)
                        if isinstance(res, dict) and res.get("status_code"):
                            st.error(res)
                        else:
                            st.success("Texto enriquecido guardado.")
                            st.rerun()

                if isinstance(sf_block.get("text_variants"), list):
                    st.markdown("**Variantes**")
                    variants_raw = "\n".join([str(v) for v in sf_block.get("text_variants") if v is not None])
                    variants_txt = st.text_area(
                        "Variantes (una por línea)",
                        value=variants_raw,
                        key=f"sf-variants-{selected_key_raw}-{sf_block_id}",
                        height=140,
                    )
                    if st.button("Guardar variantes", key=f"sf-save-variants-{selected_key_raw}-{sf_block_id}", use_container_width=True, disabled=is_locked):
                        variants_list = [v.strip() for v in (variants_txt or "").split("\n") if v.strip()]
                        with st.spinner("Guardando…"):
                            res = _patch_subflow_text_variants(selected_key_raw, sf_block_id, variants_list)
                        if isinstance(res, dict) and res.get("status_code"):
                            st.error(res)
                        else:
                            st.success("Variantes guardadas.")
                            st.rerun()

                if sf_type in {"buttons", "options"}:
                    st.markdown("**Opciones**")
                    existing = sf_block.get("options") if isinstance(sf_block.get("options"), list) else []
                    patched: list[dict] = []
                    for o in existing:
                        if not isinstance(o, dict):
                            continue
                        oid = str(o.get("id") or o.get("value") or "").strip()
                        if not oid:
                            continue
                        label = o.get("label")
                        st.markdown(f"- ID: `{oid}`")
                        if isinstance(label, dict):
                            lbl_patch = {}
                            for lang in sf_langs:
                                lbl_patch[lang] = st.text_input(
                                    f"Label ({lang.upper()}) · {oid}",
                                    value=str(label.get(lang) or ""),
                                    key=f"sf-opt-{selected_key_raw}-{sf_block_id}-{oid}-{lang}",
                                )
                            patched.append({"id": oid, "label": lbl_patch})
                        else:
                            val = st.text_input(
                                f"Label · {oid}",
                                value=str(label or ""),
                                key=f"sf-opt-{selected_key_raw}-{sf_block_id}-{oid}",
                            )
                            patched.append({"id": oid, "label": val})

                    st.markdown("**Añadir opción**")
                    new_id = st.text_input("ID nueva opción", value="", key=f"sf-new-opt-id-{selected_key_raw}-{sf_block_id}")
                    if new_id:
                        new_labels = {}
                        for lang in sf_langs:
                            new_labels[lang] = st.text_input(
                                f"Label ({lang.upper()}) · nueva",
                                value="",
                                key=f"sf-new-opt-label-{selected_key_raw}-{sf_block_id}-{lang}",
                            )
                        if st.button("Guardar opciones", key=f"sf-save-opts-{selected_key_raw}-{sf_block_id}", use_container_width=True, disabled=is_locked):
                            payload_opts = patched + [{"id": new_id.strip(), "label": new_labels}]
                            with st.spinner("Guardando…"):
                                res = _patch_subflow_options(selected_key_raw, sf_block_id, payload_opts)
                            if isinstance(res, dict) and res.get("status_code"):
                                st.error(res)
                            else:
                                st.success("Opciones guardadas.")
                                st.rerun()
                    else:
                        if st.button("Guardar opciones", key=f"sf-save-opts-{selected_key_raw}-{sf_block_id}", use_container_width=True, disabled=is_locked):
                            with st.spinner("Guardando…"):
                                res = _patch_subflow_options(selected_key_raw, sf_block_id, patched)
                            if isinstance(res, dict) and res.get("status_code"):
                                st.error(res)
                            else:
                                st.success("Opciones guardadas.")
                                st.rerun()
