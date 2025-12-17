import ChatContainer from "./ChatContainer";
import "../styles/window.css";

export default function ChatWindow({ apiUrl, widgetToken, runtime, strings, onClose }) {
  const position = runtime?.tokens?.bubble?.position || runtime?.visual?.position || "bottom-right";
  const size = runtime?.tokens?.bubble?.size || runtime?.visual?.size || "md";
  return (
    <div className={`chat-window-wrapper pos-${position}`}>
      <div className={`chat-window size-${size}`}>
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
          widgetToken={widgetToken}
          runtime={runtime}
          strings={strings}
        />
      </div>
    </div>
  );
}
