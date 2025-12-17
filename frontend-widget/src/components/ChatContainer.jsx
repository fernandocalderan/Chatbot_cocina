import { useState, useEffect, useRef } from "react";
import ChatHeader from "./ChatHeader";
import ChatMessages from "./ChatMessages";
import ChatOptions from "./ChatOptions";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";
import { createWidgetSession, sendWidgetMessage, fetchAgendaSlots, confirmAgendaSlot } from "../api/widgetApi";

function sessionStorageKey(tenantId) {
  return `opn_widget_session_id:${tenantId}`;
}

function resolveText(value, fallbackLang) {
  if (!value) return "";
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    return value[fallbackLang] || value.es || value.en || value.pt || value.ca || Object.values(value)[0] || "";
  }
  return String(value);
}

function humanDelay() {
  const min = 200;
  const max = 600;
  return new Promise((resolve) => {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    setTimeout(resolve, delay);
  });
}

function formatSlotLabel(value, lang) {
  if (!value) return "";
  const date = new Date(value.includes("T") ? `${value}:00` : value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(lang || "es", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ChatContainer({ apiUrl, widgetToken, runtime, strings }) {
  const [messages, setMessages] = useState([]);
  const [options, setOptions] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [widgetState, setWidgetState] = useState("INICIADA");
  const [slots, setSlots] = useState([]);

  const messagesRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTo({ top: messagesRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, typing]);

  useEffect(() => {
    const welcome = resolveText(runtime?.messages?.welcome, runtime?.messages?.language || "es");
    if (welcome) {
      setMessages([{ role: "bot", text: welcome }]);
    }
  }, [runtime]);

  useEffect(() => {
    const tenantId = runtime?.tenant?.id;
    if (!tenantId) return;
    const key = sessionStorageKey(tenantId);
    const existing = localStorage.getItem(key);
    if (existing) {
      setSessionId(existing);
      return;
    }
    (async () => {
      const created = await createWidgetSession(apiUrl, widgetToken, tenantId);
      if (created?.session_id) {
        localStorage.setItem(key, created.session_id);
        setSessionId(created.session_id);
        setWidgetState(created.state || "INICIADA");
      }
    })();
  }, [apiUrl, widgetToken, runtime]);

  async function maybeLoadSlots(nextState) {
    if (nextState !== "CITA_SOLICITADA") {
      setSlots([]);
      return;
    }
    if (!sessionId) return;
    const resp = await fetchAgendaSlots(apiUrl, widgetToken, sessionId);
    const list = Array.isArray(resp?.slots) ? resp.slots : [];
    setSlots(list);
  }

  async function sendMessage(text, kind = "text") {
    const trimmed = (text || "").trim();
    if (!trimmed) return;
    if (!sessionId) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setTyping(true);

    try {
      const data = await sendWidgetMessage(apiUrl, widgetToken, sessionId, kind, trimmed);
      if (!data) {
        const offlineText =
          resolveText(runtime?.messages?.errors?.offline, runtime?.messages?.language || "es") ||
          strings?.offlineMessage ||
          strings?.errorMessage ||
          "Nuestro asistente no está disponible.";
        setTyping(false);
        setMessages((prev) => [...prev, { role: "bot", text: offlineText }]);
        setOptions([]);
        return;
      }

      await humanDelay();
      setTyping(false);
      const msgs = Array.isArray(data.messages) ? data.messages : [];
      const btn = msgs.find((m) => m?.type === "buttons");
      const textMsg = msgs.find((m) => m?.type === "text");
      if (textMsg?.content) setMessages((prev) => [...prev, { role: "bot", text: textMsg.content }]);
      if (btn?.options) setOptions(btn.options);
      else setOptions([]);
      const nextState = data.state || "EN_CONVERSACION";
      setWidgetState(nextState);
      await maybeLoadSlots(nextState);
    } catch (error) {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text:
            resolveText(runtime?.messages?.errors?.offline, runtime?.messages?.language || "es") ||
            strings?.offlineMessage ||
            strings?.errorMessage ||
            "Nuestro asistente no está disponible.",
        },
      ]);
      setOptions([]);
    }
  }

  async function confirmSlot(slot) {
    if (!sessionId) return;
    const start = slot?.start;
    if (!start) return;
    setTyping(true);
    const data = await confirmAgendaSlot(apiUrl, widgetToken, sessionId, start);
    await humanDelay();
    setTyping(false);
    if (!data) return;
    const msgs = Array.isArray(data.messages) ? data.messages : [];
    const btn = msgs.find((m) => m?.type === "buttons");
    const textMsg = msgs.find((m) => m?.type === "text");
    if (textMsg?.content) setMessages((prev) => [...prev, { role: "bot", text: textMsg.content }]);
    if (btn?.options) setOptions(btn.options);
    else setOptions([]);
    const nextState = data.state || widgetState;
    setWidgetState(nextState);
    await maybeLoadSlots(nextState);
  }

  const headerTitle = runtime?.tenant?.display_name || strings?.headerTitle || "Chat";
  const logoUrl = runtime?.visual?.logo_url;

  return (
    <div className="chat-container">
      <ChatHeader
        title={headerTitle}
        subtitle={null}
        status={strings?.status}
        logoUrl={logoUrl}
      />

      <div className="chat-messages" ref={messagesRef}>
        <ChatMessages messages={messages} />
        {typing && <TypingIndicator />}
        {options.length > 0 && <ChatOptions options={options} onSelect={(opt) => sendMessage(opt, "button")} />}
          {widgetState === "CITA_SOLICITADA" && slots.length > 0 && (
          <div className="options-container">
            {slots.slice(0, 10).map((s) => (
              <span key={s.start} className="option-chip" onClick={() => confirmSlot(s)}>
                {formatSlotLabel(s.start, runtime?.messages?.language || "es")}
              </span>
            ))}
          </div>
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
