from __future__ import annotations

import os

import streamlit as st

from auth import ensure_login
from nav import render_sidebar, show_flash, nav_v2_enabled
from api_client import (
    fetch_flow,
    get_quota_status,
    get_ia_metrics,
    get_tenant_kpis,
    get_tenant_config,
    get_automation_materials,
    save_automation_materials,
    publish_automation_materials,
    rollback_automation_materials,
    list_files,
    upload_tenant_file,
    extract_tenant_file,
)
from utils import load_styles, empty_state, metric_card, render_quota_banner, pill

st.set_page_config(page_title="Automatización", page_icon="🤖", layout="wide")
load_styles()
ensure_login()
if not nav_v2_enabled():
    st.switch_page("pages/04_Automatizacion.py")
    st.stop()
render_sidebar()

show_flash()

st.title("Automatización")
st.caption("Ajusta cómo responde el asistente y el nivel de automatización.")

_TAB_KEY_TO_LABEL = {
    "flujo": "Cómo responde el asistente",
    "branding": "Imagen y mensajes",
    "nivel": "Nivel de automatización",
}
_TAB_LABEL_TO_KEY = {v: k for k, v in _TAB_KEY_TO_LABEL.items()}


def _qp_get(key: str) -> str | None:
    try:
        value = st.query_params.get(key)
        if isinstance(value, list):
            value = value[0] if value else None
        return str(value) if value else None
    except Exception:
        return None


def _qp_set(key: str, value: str):
    try:
        st.query_params[key] = value
    except Exception:
        pass


def _sync_subroute_from_path():
    # Nota: no usamos subrutas tipo /automatizacion/flujo porque rompen assets de Streamlit.
    return


def _clean_url(tab_key: str):
    # Mantener query params (no tocar pathname).
    return


_sync_subroute_from_path()

tab_key = (_qp_get("tab") or st.session_state.get("_automation_tab") or "flujo").lower()
if tab_key not in _TAB_KEY_TO_LABEL:
    tab_key = "flujo"
st.session_state["_automation_tab"] = tab_key

tab_label = st.radio(
    "Automatización",
    options=list(_TAB_KEY_TO_LABEL.values()),
    index=list(_TAB_KEY_TO_LABEL.keys()).index(tab_key),
    horizontal=True,
    label_visibility="collapsed",
)
selected_key = _TAB_LABEL_TO_KEY.get(tab_label, "flujo")
if selected_key != tab_key:
    st.session_state["_automation_tab"] = selected_key
    _qp_set("tab", selected_key)
    st.rerun()

st.caption(f"Automatización > {_TAB_KEY_TO_LABEL[selected_key]}")

if selected_key == "flujo":
    st.subheader("Cómo responde el asistente")
    st.caption("Configura materiales del flujo (visual, textos, automatización) sin tocar la lógica.")

    data = get_automation_materials() or {}
    draft = data.get("draft") if isinstance(data, dict) else None
    published = data.get("published") if isinstance(data, dict) else None
    visual = (data.get("visual") if isinstance(data, dict) else None) or {}
    versions = data.get("versions") if isinstance(data.get("versions"), list) else []
    available_flows = data.get("available_flows") if isinstance(data.get("available_flows"), list) else []

    current = draft or published or {}
    content = current.get("content") if isinstance(current.get("content"), dict) else {}
    automation = current.get("automation") if isinstance(current.get("automation"), dict) else {}
    knowledge_files_current = current.get("knowledge_files") if isinstance(current.get("knowledge_files"), list) else []

    tabs = st.tabs(["Visual", "Cómo habla", "Automatización", "Flujo activo", "Archivos"])

    with tabs[0]:
        st.markdown("### Visual del widget")
        col1, col2 = st.columns(2)
        primary = col1.text_input("Color primario", value=str(visual.get("primary_color") or "#6B5B95"), key="vis_primary")
        secondary = col2.text_input("Color secundario", value=str(visual.get("secondary_color") or "#EDE9FE"), key="vis_secondary")
        accent = col1.text_input("Color acento", value=str(visual.get("accent_color") or "#C9A24D"), key="vis_accent")
        logo_url = col2.text_input("Logo (URL)", value=str(visual.get("logo_url") or ""), key="vis_logo")
        position = col1.selectbox("Posición", ["bottom-right", "bottom-left"], index=0 if str(visual.get("position") or "bottom-right") == "bottom-right" else 1, key="vis_pos")
        size = col2.selectbox("Tamaño", ["sm", "md", "lg"], index=["sm", "md", "lg"].index(str(visual.get("size") or "md")), key="vis_size")
        tone = col1.selectbox("Tono visual", ["serio", "cercano"], index=0 if str(visual.get("tone") or "serio") == "serio" else 1, key="vis_tone")
        font_family = col2.text_input("Fuente (familia)", value=str(visual.get("font_family") or "Inter"), key="vis_font_family")
        font_size = col1.slider("Tamaño base (px)", min_value=12, max_value=18, value=int(visual.get("font_size") or 14), key="vis_font_size")
        border_radius = col2.slider("Radio de burbuja (px)", min_value=8, max_value=24, value=int(visual.get("border_radius") or 16), key="vis_radius")
        if logo_url:
            st.image(logo_url, width=140)

    with tabs[1]:
        st.markdown("### Cómo habla el asistente")
        welcome = st.text_area("Mensaje de bienvenida", value=str(content.get("welcome") or ""), height=90, key="mat_welcome")
        closing = st.text_area("Mensaje de cierre", value=str(content.get("closing") or ""), height=70, key="mat_closing")
        lang = st.selectbox("Idioma por defecto", ["es", "pt", "en", "ca"], index=["es", "pt", "en", "ca"].index(str(content.get("language") or "es")), key="mat_lang")
        tone_conv = st.selectbox("Tono conversacional", ["serio", "cercano"], index=0 if str(content.get("tone") or "serio") == "serio" else 1, key="mat_tone")

        st.markdown("### Errores")
        err_offline = st.text_input("Mensaje sin conexión", value=str((content.get("errors") or {}).get("offline") or ""), key="mat_err_offline")
        err_generic = st.text_input("Mensaje genérico", value=str((content.get("errors") or {}).get("generic") or ""), key="mat_err_generic")

        st.divider()
        st.markdown("### Preguntas y botones (avance guiado)")
        with st.expander("Cargar bloques del flujo activo", expanded=False):
            if st.button("Cargar bloques", use_container_width=True):
                with st.spinner("Cargando…"):
                    flow = fetch_flow()
                if isinstance(flow, dict) and isinstance(flow.get("flow"), dict):
                    st.session_state["_flow_blocks"] = flow["flow"].get("blocks", {})
                else:
                    empty_state("No pudimos cargar el flujo", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")

        blocks = st.session_state.get("_flow_blocks") or {}
        if isinstance(blocks, dict) and blocks:
            for block_id, block in list(blocks.items())[:20]:
                if not isinstance(block, dict):
                    continue
                text = block.get("text")
                if not text and block.get("type") not in {"buttons", "options"}:
                    continue
                title = block_id
                snippet = ""
                if isinstance(text, dict):
                    snippet = str(text.get("es") or "")[:60]
                elif isinstance(text, str):
                    snippet = text[:60]
                with st.expander(f"{title}{(' — ' + snippet) if snippet else ''}", expanded=False):
                    if text:
                        st.text_area("Texto (ES)", value=str(text.get("es") if isinstance(text, dict) else text), key=f"q-{block_id}")
                    options = block.get("options") if isinstance(block.get("options"), list) else []
                    if options:
                        for idx, opt in enumerate(options):
                            label = opt.get("label") if isinstance(opt, dict) else opt
                            label_es = label.get("es") if isinstance(label, dict) else label
                            st.text_input(f"Botón {idx+1}", value=str(label_es or ""), key=f"b-{block_id}-{idx}")

    with tabs[2]:
        st.markdown("### Automatización")
        ai_level = st.selectbox("Nivel de IA", ["off", "low", "medium", "high"], index=["off", "low", "medium", "high"].index(str(automation.get("ai_level") or "medium")), key="auto_level")
        saving_mode = st.toggle("Modo ahorro", value=bool(automation.get("saving_mode") or False), key="auto_saving")
        human_fallback = st.toggle("Fallback humano", value=bool(automation.get("human_fallback") if "human_fallback" in automation else True), key="auto_fallback")
        max_resp = st.slider("Tiempo máximo de respuesta (seg)", min_value=3, max_value=20, value=int(automation.get("max_response_seconds") or 8), key="auto_resp")
        st.markdown("### Uso de IA por pasos")
        steps = ["intent_extraction", "ai_reply", "ai_extract", "ai_generate"]
        selected_steps = []
        existing_steps = automation.get("ai_steps") if isinstance(automation.get("ai_steps"), list) else []
        for step in steps:
            if st.checkbox(step, value=step in existing_steps, key=f"auto_step_{step}"):
                selected_steps.append(step)

    with tabs[3]:
        st.markdown("### Flujo activo")
        flow_ids = [f.get("id") for f in available_flows if isinstance(f, dict)]
        flow_labels = {f.get("id"): f.get("label") for f in available_flows if isinstance(f, dict)}
        current_flow = str(current.get("flow_id") or (flow_ids[0] if flow_ids else "base_plan_fixed"))
        if flow_ids:
            idx = flow_ids.index(current_flow) if current_flow in flow_ids else 0
            selected_flow = st.selectbox("Selecciona el flujo", flow_ids, index=idx, format_func=lambda v: flow_labels.get(v, v))
        else:
            selected_flow = st.text_input("Flow ID", value=current_flow)
        st.info("Los cambios afectan solo nuevas conversaciones. Las sesiones activas no se alteran.")

    with tabs[4]:
        st.markdown("### Archivos (materiales de aprendizaje)")
        st.caption(
            "Sube PDFs/imagenes y selecciona cuáles puede usar la IA como contexto. "
            "PDFs: extracción automática. Imágenes: usa ‘Extraer con IA’."
        )

        uploaded = st.file_uploader("Subir archivo", type=["pdf", "png", "jpg", "jpeg"], key="kb-upload")
        if uploaded is not None and st.button("Subir", key="kb-upload-btn"):
            with st.spinner("Subiendo…"):
                res = upload_tenant_file(uploaded)
            if isinstance(res, dict) and res.get("file_id"):
                st.success("Archivo subido.")
                st.rerun()
            else:
                st.error(res)

        files = list_files() or []
        file_by_id = {f.get("file_id"): f for f in files if isinstance(f, dict) and f.get("file_id")}
        file_ids = list(file_by_id.keys())

        if not file_ids:
            empty_state("Sin archivos", "Sube un PDF o una imagen para usarla como material.", icon="📎")
        else:
            def _label(fid: str) -> str:
                f = file_by_id.get(fid) or {}
                name = f.get("original_filename") or fid
                ctype = f.get("content_type") or ""
                return f"{name} ({ctype})"

            kb_default = [fid for fid in knowledge_files_current if fid in file_by_id]
            selected_kb = st.multiselect(
                "Archivos usados por IA (knowledge base)",
                options=file_ids,
                default=kb_default,
                format_func=_label,
                key="kb-files",
            )

            st.markdown("#### Estado de extracción")
            use_ai_images = st.toggle("Usar IA para extraer texto de imágenes", value=True, key="kb-use-ai-images")
            for fid in selected_kb:
                f = file_by_id.get(fid) or {}
                extracted_key = f.get("extracted_text_key")
                extracted_method = f.get("extracted_method") or "n/d"
                ctype = str(f.get("content_type") or "")
                with st.expander(_label(fid), expanded=False):
                    st.caption(f"ID: `{fid}`")
                    if extracted_key:
                        st.success(f"Extracción OK ({extracted_method})")
                        if f.get("extracted_preview"):
                            st.text_area(
                                "Preview (recorte)",
                                value=str(f.get("extracted_preview") or ""),
                                height=140,
                                disabled=True,
                                key=f"kb-preview-{fid}",
                            )
                    else:
                        st.warning("Sin extracción todavía.")
                        can_ai = ctype in {"image/png", "image/jpeg"} and use_ai_images
                        if st.button("Extraer ahora", key=f"kb-extract-{fid}"):
                            with st.spinner("Extrayendo…"):
                                res = extract_tenant_file(fid, use_ai=bool(can_ai))
                            if isinstance(res, dict) and res.get("extracted"):
                                st.success("Extracción completada.")
                                st.rerun()
                            else:
                                st.error(res)

    st.divider()
    c1, c2, c3 = st.columns([0.4, 0.4, 0.2])
    if c1.button("Guardar borrador", use_container_width=True):
        questions = {}
        buttons = {}
        blocks = st.session_state.get("_flow_blocks") or {}
        if isinstance(blocks, dict):
            for block_id, block in blocks.items():
                if not isinstance(block, dict):
                    continue
                q_key = f"q-{block_id}"
                if q_key in st.session_state and st.session_state[q_key].strip():
                    questions[block_id] = st.session_state[q_key].strip()
                options = block.get("options") if isinstance(block.get("options"), list) else []
                labels = []
                for idx, _opt in enumerate(options):
                    b_key = f"b-{block_id}-{idx}"
                    if b_key in st.session_state and st.session_state[b_key].strip():
                        labels.append(st.session_state[b_key].strip())
                if labels:
                    buttons[block_id] = labels

        payload = {
            "flow_id": selected_flow,
            "knowledge_files": st.session_state.get("kb-files") or knowledge_files_current or [],
            "content": {
                "welcome": welcome,
                "closing": closing,
                "language": lang,
                "tone": tone_conv,
                "errors": {"offline": err_offline, "generic": err_generic},
                "questions": questions,
                "buttons": buttons,
            },
            "automation": {
                "ai_level": ai_level,
                "saving_mode": saving_mode,
                "human_fallback": human_fallback,
                "max_response_seconds": max_resp,
                "ai_steps": selected_steps,
            },
            "visual": {
                "primary_color": primary,
                "secondary_color": secondary,
                "accent_color": accent,
                "logo_url": logo_url,
                "position": position,
                "size": size,
                "tone": tone,
                "font_family": font_family,
                "font_size": font_size,
                "border_radius": border_radius,
            },
        }
        with st.spinner("Guardando borrador…"):
            res = save_automation_materials(payload)
        if isinstance(res, dict) and res.get("status_code"):
            empty_state("No pudimos guardar ahora", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
        else:
            st.success("Borrador guardado.")

    if c2.button("Publicar cambios", use_container_width=True):
        with st.spinner("Publicando…"):
            res = publish_automation_materials()
        if isinstance(res, dict) and res.get("status_code"):
            empty_state("No pudimos publicar ahora", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
        else:
            st.success("Publicado. Afecta nuevas conversaciones.")
            st.rerun()

    if versions:
        with c3:
            version_ids = [v.get("version") for v in versions if v.get("version")]
            if version_ids:
                rollback_ver = st.selectbox("Rollback", version_ids, key="rollback_ver")
                if st.button("Restaurar", use_container_width=True):
                    with st.spinner("Restaurando…"):
                        out = rollback_automation_materials(int(rollback_ver))
                    if isinstance(out, dict) and out.get("status_code"):
                        empty_state("No pudimos restaurar ahora", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
                    else:
                        st.success("Rollback publicado.")
                        st.rerun()

elif selected_key == "branding":
    st.subheader("Imagen y mensajes")
    st.caption("Controla cómo se presenta el asistente al cliente final.")

    cfg = get_tenant_config() or {}
    if isinstance(cfg, dict) and cfg.get("status_code"):
        empty_state("No pudimos cargar la configuración", "Estamos cargando la información. El asistente sigue activo.", icon="⚠️")
    else:
        name = st.session_state.get("tenant_name") or cfg.get("name") or "Tu negocio"
        logo = st.session_state.get("tenant_logo_url") or cfg.get("logo_url")
        lang = st.session_state.get("tenant_language") or cfg.get("language") or "es"
        tz = st.session_state.get("tenant_timezone") or cfg.get("timezone") or "Europe/Madrid"
        tenant_id = st.session_state.get("tenant_id") or cfg.get("tenant_id") or os.getenv("PANEL_TENANT_ID", "<TENANT_ID>")

        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown("### Identidad")
            st.text_input("Nombre comercial", value=str(name), disabled=True)
            st.text_input("Idioma", value=str(lang).upper(), disabled=True)
            st.text_input("Zona horaria", value=str(tz), disabled=True)
        with c2:
            st.markdown("### Logo")
            if logo:
                st.image(logo, width=170)
            else:
                empty_state("Sin logo", "Puedes añadirlo con soporte o desde el panel de administración.", icon="🖼️")

        st.markdown("### Mensajes")
        st.caption("Los mensajes se ajustan en “Cómo responde el asistente”.")
        st.divider()
        st.markdown("### Instalación del widget")
        st.caption("La instalación (snippet + token) se gestiona en Configuración.")
        if st.button("Abrir Configuración", use_container_width=True):
            st.session_state["_config_tab"] = "widget"
            st.switch_page("pages/configuracion.py")

else:
    st.subheader("Nivel de automatización")
    st.caption("Control simplificado del uso de IA.")

    st.info("El asistente adapta su nivel de automatización según tu plan.")

    tenant_id = st.session_state.get("tenant_id")
    quota = get_quota_status() or {}
    quota_status = quota.get("quota_status") if isinstance(quota, dict) else {}
    if not isinstance(quota_status, dict):
        quota_status = {}

    kpis = get_tenant_kpis() or {}
    kpi_data = kpis.get("kpis") if isinstance(kpis, dict) and isinstance(kpis.get("kpis"), dict) else {}
    ia_metrics = get_ia_metrics(tenant_id) if tenant_id else {}
    monthly = ia_metrics.get("monthly") if isinstance(ia_metrics, dict) and isinstance(ia_metrics.get("monthly"), dict) else {}

    spent = float((monthly.get("total_cost_eur") if isinstance(monthly, dict) else 0.0) or 0.0)
    limit = float((quota_status.get("limit_eur") if isinstance(quota_status, dict) else 0.0) or (kpi_data.get("ai_limit_eur") or 0.0) or 0.0)
    mode = str((quota_status.get("mode") if isinstance(quota_status, dict) else "") or "ACTIVE").upper()

    needs_upgrade = bool(quota_status.get("needs_upgrade_notice")) if isinstance(quota_status, dict) else False
    render_quota_banner(quota_status, needs_upgrade=needs_upgrade)

    estado = "Activo" if mode == "ACTIVE" else "Ahorro"
    tone = "success" if estado == "Activo" else "warning"
    metric_card("Estado del asistente", estado, subtitle="", accent="#0D9488" if estado == "Activo" else "#B45309")

    pct = 0.0
    if limit:
        try:
            pct = min(max((spent / limit) * 100.0, 0.0), 100.0)
        except Exception:
            pct = 0.0
    usage_level = "Bajo" if pct < 50 else ("Medio" if pct < 80 else "Alto")
    st.markdown(pill(f"Uso del límite: {usage_level}", tone=tone), unsafe_allow_html=True)
    st.progress(pct / 100.0 if limit else 0.0)

    if estado != "Activo":
        empty_state("El asistente sigue activo", "Podrás seguir captando oportunidades, pero algunas respuestas pueden simplificarse.", icon="✨")
