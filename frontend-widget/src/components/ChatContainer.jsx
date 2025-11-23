import { useState, useEffect, useRef } from "react";
import ChatHeader from "./ChatHeader";
import ChatMessages from "./ChatMessages";
import ChatOptions from "./ChatOptions";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";

export default function ChatContainer({ apiUrl, tenantTheme, strings }) {
  const [messages, setMessages] = useState([]);
  const [options, setOptions] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);

  const messagesRef = useRef(null);
  const sessionIdRef = useRef(null);

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

  async function sendMessage(text) {
    const trimmed = (text || "").trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setTyping(true);

    try {
      const res = await fetch(`${apiUrl}/chat/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, session_id: sessionIdRef.current }),
      });

      const data = await res.json();

      setTyping(false);
      setMessages((prev) => [...prev, { role: "bot", text: data.text }]);

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
        { role: "bot", text: strings?.errorMessage || "No pude responder. Intenta de nuevo." },
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
