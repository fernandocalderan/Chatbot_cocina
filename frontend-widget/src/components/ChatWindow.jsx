import ChatContainer from "./ChatContainer";
import "../styles/window.css";

export default function ChatWindow({ apiUrl, apiKey, tenantId, tenantTheme, strings, onClose }) {
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
        <ChatContainer apiUrl={apiUrl} apiKey={apiKey} tenantId={tenantId} tenantTheme={tenantTheme} strings={strings} />
      </div>
    </div>
  );
}
