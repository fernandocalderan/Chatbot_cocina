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
  apiKey: undefined,
  tenantId: undefined,
  headerTitle: undefined,
  headerSubtitle: undefined,
  widgetToken: undefined,
};

function normalizeConfig(options = {}) {
  const safeOptions = options && typeof options === "object" ? options : {};
  const config = { ...DEFAULT_CONFIG, ...safeOptions };
  config.language = resolveLanguage(config.language);
  config.startOpen = Boolean(config.startOpen);
  if (config.apiKey && typeof config.apiKey === "string") {
    config.apiKey = config.apiKey.trim();
  } else {
    config.apiKey = undefined;
  }
  if (config.tenantId && typeof config.tenantId === "string") {
    config.tenantId = config.tenantId.trim();
  } else {
    config.tenantId = undefined;
  }
  if (config.widgetToken && typeof config.widgetToken === "string") {
    config.widgetToken = config.widgetToken.trim();
  } else {
    config.widgetToken = undefined;
  }
  return config;
}

async function fetchTenantConfig(apiUrl, apiKey, tenantId) {
  if (!tenantId) return null;
  try {
    const headers = {};
    if (apiKey) {
      headers["Authorization"] = `Bearer ${apiKey}`;
      headers["x-api-key"] = apiKey;
    }
    headers["Idempotency-Key"] = `${tenantId}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const res = await fetch(`${apiUrl}/v1/tenant/config`, { headers });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error("ChatWidget: no se pudo obtener la config del tenant", e);
    return null;
  }
}

window.ChatWidget = {
  init: async (options = {}) => {
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

    const tenantCfg = await fetchTenantConfig(config.apiUrl, config.apiKey, config.tenantId);
    if (tenantCfg) {
      if (!config.tenantTheme && tenantCfg.theme) config.tenantTheme = tenantCfg.theme;
      if (!options.language && tenantCfg.language) config.language = tenantCfg.language;
      if (!config.headerTitle && tenantCfg.texts?.header_title) config.headerTitle = tenantCfg.texts.header_title;
      if (!config.headerSubtitle && tenantCfg.texts?.header_subtitle)
        config.headerSubtitle = tenantCfg.texts.header_subtitle;
    }

    const strings = getStrings(config.language);

    createRoot(root).render(
      <React.StrictMode>
        <FloatingButton
          apiUrl={config.apiUrl}
          apiKey={config.apiKey}
          widgetToken={config.widgetToken}
          tenantId={config.tenantId}
          tenantTheme={config.tenantTheme}
          startOpen={config.startOpen}
          strings={{ ...strings, headerTitle: config.headerTitle, headerSubtitle: config.headerSubtitle }}
        />
      </React.StrictMode>,
    );
  },
};

// Auto-init en entorno local si no se invoca explícitamente
if (import.meta.env.DEV) {
  const root = document.getElementById("widget-root");
  if (root) {
    const apiUrl = import.meta.env.VITE_API_BASE || "http://localhost:8100";
    const apiKey = import.meta.env.VITE_API_KEY;
    const tenantTheme = import.meta.env.VITE_TENANT_THEME || "orange";
    const language = import.meta.env.VITE_LANGUAGE || "es";
    const startOpen = import.meta.env.VITE_START_OPEN === "true";
    const tenantId = import.meta.env.VITE_TENANT_ID;
    const widgetToken = import.meta.env.VITE_WIDGET_TOKEN;
    window.ChatWidget.init({ apiUrl, apiKey, tenantTheme, language, startOpen, tenantId, widgetToken });
  }
}
