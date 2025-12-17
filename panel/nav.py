import os
import streamlit as st


def nav_v2_enabled() -> bool:
    # Feature flag para activar navegación/rutas V2 de forma reversible.
    override = st.session_state.get("_panel_nav_v2")
    if isinstance(override, bool):
        return override
    raw_env = os.getenv("PANEL_NAV_V2")
    raw = str(raw_env or "").strip().lower()
    if raw in {"0", "false", "no", "off"}:
        return False
    if raw in {"1", "true", "yes", "on"}:
        return True
    # Default ON (se puede desactivar explícitamente con PANEL_NAV_V2=false).
    return True


def _log_legacy_once(from_path: str, to_path: str):
    key = "_legacy_route_warnings"
    seen = st.session_state.get(key)
    if not isinstance(seen, set):
        seen = set()
    token = f"{from_path}->{to_path}"
    if token in seen:
        return
    seen.add(token)
    st.session_state[key] = seen
    # Warning interno: solo consola/logs, no UI.
    print(f"[legacy-route] {from_path} -> {to_path}")


def set_flash(message: str):
    if message:
        st.session_state["_flash_message"] = message


def show_flash():
    msg = st.session_state.pop("_flash_message", None)
    if msg:
        st.info(msg)


def legacy_redirect(from_path: str, to_page: str, flash_message: str | None = None):
    _log_legacy_once(from_path, to_page)
    if flash_message:
        set_flash(flash_message)
    # Permite fijar tab interno de Automatización antes del redirect.
    automation_tab = st.session_state.pop("_legacy_automation_tab", None)
    if automation_tab:
        st.session_state["_automation_tab"] = automation_tab
    try:
        st.switch_page(to_page)
    except Exception:
        # fallback (no visible error)
        pass


def legacy_redirect_with_tab(from_path: str, to_page: str, tab: str, flash_message: str | None = None):
    st.session_state["_legacy_automation_tab"] = tab
    legacy_redirect(from_path, to_page, flash_message=flash_message)


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="op-sidebar-brand">OPUNNENCE FLOW</div>', unsafe_allow_html=True)
        st.markdown('<div class="op-sidebar-sep"></div>', unsafe_allow_html=True)

        if nav_v2_enabled():
            st.page_link("pages/inicio.py", label="Inicio", icon=":material/home:")
            st.page_link("pages/oportunidades.py", label="Oportunidades", icon=":material/insights:")
            st.page_link("pages/agenda.py", label="Agenda", icon=":material/event_note:")
        else:
            st.page_link("pages/00_Inicio.py", label="Inicio", icon=":material/home:")
            st.page_link("pages/02_Oportunidades.py", label="Oportunidades", icon=":material/insights:")
            st.page_link("pages/03_Agenda.py", label="Agenda", icon=":material/event_note:")

        st.markdown('<div class="op-sidebar-sep"></div>', unsafe_allow_html=True)

        if nav_v2_enabled():
            st.page_link("pages/automatizacion.py", label="Automatización", icon=":material/auto_awesome:")
            st.page_link("pages/configuracion.py", label="Configuración", icon=":material/settings:")
        else:
            st.page_link("pages/04_Automatizacion.py", label="Automatización", icon=":material/auto_awesome:")
            st.page_link("pages/05_Configuracion.py", label="Configuración", icon=":material/settings:")
