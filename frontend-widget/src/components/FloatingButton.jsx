import { useState } from "react";
import ChatWindow from "./ChatWindow";
import "../styles/floating.css";

export default function FloatingButton({ apiUrl, widgetToken, runtime, startOpen, strings }) {
  const [open, setOpen] = useState(Boolean(startOpen));
  const position = runtime?.tokens?.bubble?.position || runtime?.visual?.position || "bottom-right";
  const logoUrl = runtime?.visual?.logo_url;
  const [hasUnread, setHasUnread] = useState(Boolean(runtime?.messages?.welcome));

  return (
    <>
      {!open && (
        <button
          className={`floating-button pos-${position}${hasUnread ? " has-unread" : ""}`}
          onClick={() => {
            setOpen(true);
            setHasUnread(false);
          }}
          aria-label={strings?.openLabel || "Abrir chat"}
          title={strings?.openLabel || "Abrir chat"}
        >
          {logoUrl ? (
            <img src={logoUrl} alt="" className="floating-logo" />
          ) : (
            <span className="floating-icon" aria-hidden="true">💬</span>
          )}
        </button>
      )}

      {open && (
        <ChatWindow
          apiUrl={apiUrl}
          widgetToken={widgetToken}
          runtime={runtime}
          strings={strings}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}
