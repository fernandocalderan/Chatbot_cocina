import ChatContainer from "./ChatContainer";
import "../styles/window.css";

export default function ChatWindow({ apiUrl, tenantTheme, strings, onClose }) {
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
        <ChatContainer apiUrl={apiUrl} tenantTheme={tenantTheme} strings={strings} />
      </div>
    </div>
  );
}
