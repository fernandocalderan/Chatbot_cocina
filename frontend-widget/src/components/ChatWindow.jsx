import ChatContainer from "./ChatContainer";
import "../styles/window.css";

export default function ChatWindow({ apiUrl, apiKey, widgetToken, tenantId, tenantTheme, logoUrl, strings, onClose }) {
  return (
    <div className="chat-window-wrapper">
      <div className="chat-window" data-theme={tenantTheme}>
        <button
          className="chat-close"
          onClick={onClose}
          aria-label={strings?.closeLabel || "Cerrar chat"}
          title={strings?.closeLabel || "Cerrar chat"}
        >
          ✕
        </button>
        <ChatContainer
          apiUrl={apiUrl}
          apiKey={apiKey}
          widgetToken={widgetToken}
          tenantId={tenantId}
          tenantTheme={tenantTheme}
          logoUrl={logoUrl}
          strings={strings}
        />
      </div>
    </div>
  );
}
