import { useState } from "react";
import ChatWindow from "./ChatWindow";
import "../styles/floating.css";

export default function FloatingButton({ apiUrl, apiKey, tenantId, tenantTheme, startOpen, strings }) {
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
          tenantId={tenantId}
          tenantTheme={tenantTheme}
          strings={strings}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  );
}
