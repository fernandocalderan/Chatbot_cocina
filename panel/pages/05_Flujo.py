import json
import streamlit as st

from api_client import fetch_flow, update_flow
from auth import ensure_login
from utils import load_styles

load_styles()
if "token" not in st.session_state:
    st.switch_page("auth.py")
ensure_login()

st.title("Editor de flujo")

if st.button("Cargar flujo"):
    flow = fetch_flow()
    if flow and "flow" in flow:
        st.session_state["flow_data"] = flow["flow"]
    else:
        st.warning("No se pudo cargar el flujo.")

flow_data = st.session_state.get("flow_data")

if flow_data:
    blocks = flow_data.get("blocks", {})
    st.subheader(f"Bloques ({len(blocks)})")
    for block_id, block in blocks.items():
        with st.expander(f"{block_id} · {block.get('type')}"):
            st.write("Tipo:", block.get("type"))
            st.write("Textos:")
            texts = block.get("text") or {}
            st.json(texts)
            if block.get("options"):
                st.write("Opciones:")
                st.json(block.get("options"))

            if st.button("Editar bloque", key=f"edit_{block_id}"):
                st.session_state["editing_block"] = block_id

    editing = st.session_state.get("editing_block")
    if editing and editing in blocks:
        st.divider()
        st.subheader(f"Editar bloque: {editing}")
        block = blocks[editing]
        texts = block.get("text") or {}
        options = block.get("options") or []

        col1, col2 = st.columns(2)
        text_es = col1.text_area("Texto (es)", value=texts.get("es", ""))
        text_en = col2.text_area("Texto (en)", value=texts.get("en", ""))
        text_ca = col1.text_area("Texto (ca)", value=texts.get("ca", ""))
        text_pt = col2.text_area("Texto (pt)", value=texts.get("pt", ""))

        options_raw = st.text_area(
            "Opciones (JSON)",
            value=json.dumps(options, ensure_ascii=False, indent=2),
            help="Lista de opciones como JSON",
            height=200,
        )

        if st.button("Guardar bloque"):
            try:
                new_options = json.loads(options_raw) if options_raw.strip() else []
                block["text"] = {"es": text_es, "en": text_en, "ca": text_ca, "pt": text_pt}
                block["options"] = new_options
                flow_data["blocks"][editing] = block
                res = update_flow(flow_data)
                if res:
                    st.success("Bloque guardado y flujo actualizado.")
            except json.JSONDecodeError:
                st.error("Opciones no son JSON válido.")
