import { useState, useEffect, useRef } from "react";
import ChatHeader from "./ChatHeader";
import ChatMessages from "./ChatMessages";
import ChatOptions from "./ChatOptions";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";

export default function ChatContainer({ apiUrl, apiKey, widgetToken, tenantId, tenantTheme, logoUrl, strings }) {
  const [messages, setMessages] = useState([]);
  const [options, setOptions] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [token, setToken] = useState(widgetToken || localStorage.getItem("widget_token") || "");

  const messagesRef = useRef(null);
  const sessionIdRef = useRef(null);
  const refreshTimerRef = useRef(null);

  useEffect(() => {
    let sid = localStorage.getItem("session_id");
    if (!sid && window.crypto?.randomUUID) {
      sid = window.crypto.randomUUID();
      localStorage.setItem("session_id", sid);
    } else if (!sid) {
      sid = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      localStorage.setItem("session_id", sid);
    }
    sessionIdRef.current = sid;
  }, []);

  // Auto-scroll
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, typing]);

  function decodeExp(jwt) {
    if (!jwt) return null;
    try {
      const payload = JSON.parse(atob(jwt.split(".")[1] || ""));
      if (!payload.exp) return null;
      return Number(payload.exp) * 1000;
    } catch (err) {
      console.warn("ChatWidget: no se pudo decodificar el token", err);
      return null;
    }
  }

  async function refreshToken() {
    if (!token || !tenantId) return;
    try {
      const res = await fetch(`${apiUrl}/v1/tenant/widget/token/renew`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          "X-Tenant-ID": tenantId,
        },
        body: JSON.stringify({ ttl_minutes: 30 }),
      });
      if (!res.ok) return;
      const data = await res.json();
      if (data.token) {
        setToken(data.token);
        localStorage.setItem("widget_token", data.token);
      }
    } catch (err) {
      console.warn("ChatWidget: no se pudo renovar el token", err);
    }
  }

  useEffect(() => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
    const expMs = decodeExp(token);
    if (!expMs) return;
    const now = Date.now();
    const leadMs = Math.max(expMs - now - 5 * 60 * 1000, 10_000);
    refreshTimerRef.current = setTimeout(refreshToken, leadMs);
    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current);
    };
  }, [token, tenantId, apiUrl]);

  async function sendMessage(text) {
    const trimmed = (text || "").trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setTyping(true);

    try {
      const headers = { "Content-Type": "application/json" };
      if (apiKey) {
        headers["x-api-key"] = apiKey;
        headers["Authorization"] = `Bearer ${apiKey}`;
      } else if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      if (tenantId) {
        headers["X-Tenant-ID"] = tenantId;
      }
      const idempotencyKey = `${sessionIdRef.current || "anon"}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      headers["Idempotency-Key"] = idempotencyKey;

      const res = await fetch(`${apiUrl}/v1/chat/send`, {
        method: "POST",
        headers,
        body: JSON.stringify({ message: trimmed, session_id: sessionIdRef.current }),
      });

      if (!res.ok) {
        const offlineText = strings?.offlineMessage || strings?.errorMessage || "Nuestro asistente no está disponible.";
        setTyping(false);
        setMessages((prev) => [...prev, { role: "bot", text: offlineText }]);
        setOptions([]);
        return;
      }

      const data = await res.json();

      setTyping(false);
      const botText = data.ai_reply || data.text || strings?.errorMessage || "No pude responder. Intenta de nuevo.";
      setMessages((prev) => [...prev, { role: "bot", text: botText }]);

      if (data.session_id && data.session_id !== sessionIdRef.current) {
        sessionIdRef.current = data.session_id;
        localStorage.setItem("session_id", data.session_id);
      }

      if (data.options) setOptions(data.options);
      else setOptions([]);
    } catch (error) {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: strings?.offlineMessage || strings?.errorMessage || "Nuestro asistente no está disponible.",
        },
      ]);
      setOptions([]);
    }
  }

  return (
    <div className="chat-container" data-theme={tenantTheme}>
      <ChatHeader
        title={strings?.headerTitle || "Chat"}
        subtitle={strings?.headerSubtitle}
        status={strings?.status}
        logoUrl={logoUrl}
      />

      <div className="chat-messages" ref={messagesRef}>
        <ChatMessages messages={messages} />
        {typing && <TypingIndicator />}
        {options.length > 0 && (
          <ChatOptions options={options} onSelect={(opt) => sendMessage(opt.id)} />
        )}
      </div>

      <ChatInput
        value={input}
        onChange={setInput}
        strings={strings}
        onSend={() => {
          sendMessage(input);
          setInput("");
        }}
      />
    </div>
  );
}
