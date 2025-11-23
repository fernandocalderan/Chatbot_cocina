import React from "react";
import { createRoot } from "react-dom/client";
import FloatingButton from "./components/FloatingButton";
import { getStrings, resolveLanguage } from "./i18n";
import "./styles/chat.css";
import "./styles/floating.css";
import "./styles/window.css";
import "./styles/theme.css";

const DEFAULT_CONFIG = {
  tenantTheme: undefined,
  language: "es",
  startOpen: false,
};

function normalizeConfig(options = {}) {
  const safeOptions = options && typeof options === "object" ? options : {};
  const config = { ...DEFAULT_CONFIG, ...safeOptions };
  config.language = resolveLanguage(config.language);
  config.startOpen = Boolean(config.startOpen);
  return config;
}

window.ChatWidget = {
  init: (options = {}) => {
    const config = normalizeConfig(options);

    if (!config.apiUrl) {
      console.error("ChatWidget: apiUrl es obligatorio");
      return;
    }

    const root = document.getElementById("widget-root");
    if (!root) {
      console.error("ChatWidget: no se encontró el elemento #widget-root");
      return;
    }

    const strings = getStrings(config.language);

    createRoot(root).render(
      <React.StrictMode>
        <FloatingButton
          apiUrl={config.apiUrl}
          tenantTheme={config.tenantTheme}
          startOpen={config.startOpen}
          strings={strings}
        />
      </React.StrictMode>,
    );
  },
};

// Auto-init en entorno local si no se invoca explícitamente
if (import.meta.env.DEV) {
  const root = document.getElementById("widget-root");
  if (root) {
    const apiUrl = import.meta.env.VITE_API_BASE || "http://localhost:9000";
    const tenantTheme = import.meta.env.VITE_TENANT_THEME || "orange";
    const language = import.meta.env.VITE_LANGUAGE || "es";
    const startOpen = import.meta.env.VITE_START_OPEN === "true";
    window.ChatWidget.init({ apiUrl, tenantTheme, language, startOpen });
  }
}
