import { useState } from "react";
import ChatWindow from "./ChatWindow";
import "../styles/floating.css";

export default function FloatingButton({ apiUrl, apiKey, widgetToken, tenantId, tenantTheme, startOpen, logoUrl, strings }) {
  const [open, setOpen] = useState(Boolean(startOpen));

  return (
    <>
      {!open && (
        <button
          className="floating-button"
          onClick={() => setOpen(true)}
          aria-label={strings?.openLabel || "Abrir chat"}
          title={strings?.openLabel || "Abrir chat"}
        >
          💬
        </button>
      )}

      {open && (
        <ChatWindow
          apiUrl={apiUrl}
          apiKey={apiKey}
          widgetToken={widgetToken}
          tenantId={tenantId}
          tenantTheme={tenantTheme}
          logoUrl={logoUrl}
          strings={strings}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}
