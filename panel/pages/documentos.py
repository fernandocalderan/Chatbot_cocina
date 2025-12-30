from __future__ import annotations

import streamlit as st

from auth import ensure_login
from nav import render_sidebar, show_flash, nav_v2_enabled
from api_client import (
    list_files,
    upload_tenant_file,
    extract_tenant_file,
    index_tenant_file,
    get_automation_materials,
    save_automation_materials,
    publish_automation_materials,
)
from utils import load_styles, empty_state, pill


st.set_page_config(page_title="Documentos", page_icon="📎", layout="wide")
load_styles()
ensure_login()
if not nav_v2_enabled():
    st.switch_page("pages/04_Automatizacion.py")
    st.stop()
render_sidebar()
show_flash()

st.title("Documentos")
st.caption("Sube archivos del negocio, extrae texto e indexa para búsqueda semántica (RAG).")


def _label(file_obj: dict) -> str:
    name = file_obj.get("original_filename") or file_obj.get("s3_key") or file_obj.get("file_id")
    ctype = file_obj.get("content_type") or "n/d"
    return f"{name} ({ctype})"

def _detail_code(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    detail = payload.get("detail")
    if isinstance(detail, dict):
        inner = detail.get("detail")
        return str(inner or "")
    if isinstance(detail, str):
        return str(detail or "")
    return ""


materials = get_automation_materials() or {}
current = (materials.get("draft") if isinstance(materials, dict) else None) or (materials.get("published") if isinstance(materials, dict) else None) or {}
knowledge_files_current = current.get("knowledge_files") if isinstance(current.get("knowledge_files"), list) else []

st.subheader("Subir")
uploaded = st.file_uploader("Archivo", type=["pdf", "png", "jpg", "jpeg", "xlsx"], key="docs-upload")
if uploaded is not None and st.button("Subir archivo", use_container_width=True):
    with st.spinner("Subiendo…"):
        res = upload_tenant_file(uploaded)
    if isinstance(res, dict) and res.get("file_id"):
        st.success("Archivo subido.")
        st.rerun()
    st.error(res)

st.divider()

st.subheader("Biblioteca")
files = list_files() or []
if not files:
    empty_state("Sin documentos", "Sube PDFs, imágenes o XLSX para alimentar el asistente.", icon="📎")
    st.stop()

file_by_id = {f.get("file_id"): f for f in files if isinstance(f, dict) and f.get("file_id")}
file_ids = [fid for fid in file_by_id.keys() if fid]

default_selected = [fid for fid in knowledge_files_current if fid in file_by_id]
selected = st.multiselect(
    "Documentos usados por la IA (KB)",
    options=file_ids,
    default=default_selected,
    format_func=lambda fid: _label(file_by_id.get(fid) or {}),
)

col_save, col_pub = st.columns(2)
if col_save.button("Guardar selección (borrador)", use_container_width=True):
    payload = {"knowledge_files": selected}
    out = save_automation_materials(payload)
    if isinstance(out, dict) and out.get("status_code"):
        st.error(out)
    else:
        st.success("Guardado en borrador.")

if col_pub.button("Publicar selección", use_container_width=True):
    with st.spinner("Publicando…"):
        out = publish_automation_materials()
    if isinstance(out, dict) and out.get("status_code"):
        st.error(out)
    else:
        st.success("Publicado.")

st.markdown("### Siguiente paso")
if st.button("Ir a Flujo (v2)", use_container_width=True):
    st.switch_page("pages/flujo_v2.py")

st.divider()

st.subheader("Estado por documento")
use_ai_images = st.toggle("Usar IA para extraer texto de imágenes", value=True)
for fid in selected:
    f = file_by_id.get(fid) or {}
    ctype = str(f.get("content_type") or "")
    extracted = bool(f.get("extracted_text_key"))
    indexed = bool(f.get("kb_indexed_at")) or bool(f.get("kb_chunks"))

    status_bits = []
    status_bits.append(pill("Texto OK", "success") if extracted else pill("Sin texto", "warning"))
    status_bits.append(pill("Index OK", "success") if indexed else pill("Sin index", "warning"))
    st.markdown(f"**{_label(f)}**  " + " ".join(status_bits), unsafe_allow_html=True)

    with st.expander("Acciones", expanded=False):
        st.caption(f"ID: `{fid}`")
        if extracted:
            st.caption(f"Método: {f.get('extracted_method') or 'n/d'}")
            if f.get("extracted_preview"):
                st.text_area("Preview", value=str(f.get("extracted_preview") or ""), height=140, disabled=True, key=f"prev-{fid}")
        else:
            can_ai = ctype in {"image/png", "image/jpeg"} and use_ai_images
            if st.button("Extraer texto", key=f"extract-{fid}"):
                with st.spinner("Extrayendo…"):
                    out = extract_tenant_file(fid, use_ai=bool(can_ai))
                if isinstance(out, dict) and out.get("extracted"):
                    st.success("Texto extraído.")
                    st.rerun()
                st.error(out)

        if st.button("Indexar para búsqueda semántica", key=f"index-{fid}"):
            with st.spinner("Indexando…"):
                out = index_tenant_file(fid, reindex=False)
            if isinstance(out, dict) and out.get("indexed"):
                st.success("Indexado OK.")
                st.rerun()
            code = _detail_code(out) if isinstance(out, dict) else ""
            if code == "ia_disabled_for_tenant":
                st.error("La IA está deshabilitada para este tenant. Actívala en Admin (Tenants → “IA habilitada”).")
            else:
                st.error(out)
