import React from "react";
import { createRoot } from "react-dom/client";
import FloatingButton from "./components/FloatingButton";
import { getStrings, resolveLanguage } from "./i18n";
import { fetchWidgetRuntime } from "./api/widgetApi";
import { applyTokens } from "./design-tokens/applyTokens";
import "./styles/chat.css";
import "./styles/floating.css";
import "./styles/window.css";
import "./styles/theme.css";

function normalizeConfig(options = {}) {
  const safeOptions = options && typeof options === "object" ? options : {};
  const config = { ...safeOptions };
  config.language = resolveLanguage(config.language || "es");
  config.startOpen = Boolean(config.startOpen);
  if (config.apiUrl && typeof config.apiUrl === "string") {
    config.apiUrl = config.apiUrl.trim().replace(/\/+$/, "");
  } else {
    config.apiUrl = undefined;
  }
  if (config.widgetToken && typeof config.widgetToken === "string") {
    config.widgetToken = config.widgetToken.trim();
  } else {
    config.widgetToken = undefined;
  }
  return config;
}

window.ChatWidget = {
  init: async (options = {}) => {
    const config = normalizeConfig(options);

    if (!config.apiUrl) {
      console.error("ChatWidget: apiUrl es obligatorio");
      return;
    }
    if (!config.widgetToken) {
      console.error("ChatWidget: widgetToken es obligatorio");
      return;
    }

    let root = document.getElementById("widget-root");
    if (!root) {
      root = document.createElement("div");
      root.id = "widget-root";
      document.body.appendChild(root);
    }

    const runtime = await fetchWidgetRuntime(config.apiUrl, config.widgetToken);
    if (!runtime) {
      console.error("ChatWidget: no se pudo obtener /v1/widget/runtime");
      return;
    }
    applyTokens(runtime);

    const cfgLang = runtime?.messages?.language || config.language;
    const strings = getStrings(resolveLanguage(cfgLang));

    createRoot(root).render(
      <React.StrictMode>
        <FloatingButton
          apiUrl={config.apiUrl}
          widgetToken={config.widgetToken}
          startOpen={config.startOpen}
          runtime={runtime}
          strings={strings}
        />
      </React.StrictMode>,
    );
  },
};

function bootstrapFromScriptTag() {
  if (window.__chatWidgetBooted) return;
  const scriptEl = document.currentScript || document.querySelector('script[data-token]');
  if (!scriptEl) return;
  const dataset = scriptEl.dataset || {};
  const apiUrl = dataset.api || dataset.apiUrl;
  const widgetToken = dataset.token;
  if (!apiUrl || !widgetToken) return;
  window.__chatWidgetBooted = true;
  const startOpen = (dataset.startOpen || "").toString().toLowerCase() === "true";
  window.ChatWidget.init({
    apiUrl,
    widgetToken,
    startOpen,
  });
}

bootstrapFromScriptTag();

// Auto-init en entorno local si no se invoca explícitamente
if (import.meta.env.DEV) {
  const root = document.getElementById("widget-root");
  if (root) {
    const apiUrl = import.meta.env.VITE_API_BASE || "http://localhost:8100";
    const language = import.meta.env.VITE_LANGUAGE || "es";
    const startOpen = import.meta.env.VITE_START_OPEN === "true";
    const widgetToken = import.meta.env.VITE_WIDGET_TOKEN;
    if (widgetToken) {
      window.ChatWidget.init({ apiUrl, language, startOpen, widgetToken });
    }
  }
}
