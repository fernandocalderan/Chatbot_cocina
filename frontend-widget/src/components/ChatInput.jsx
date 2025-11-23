export default function ChatInput({ value, onChange, onSend, strings }) {
  const placeholder = strings?.messagePlaceholder || "Escribe un mensaje...";
  const sendLabel = strings?.sendLabel || "Enviar";

  return (
    <div className="chat-input">
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
      <button onClick={onSend} aria-label={sendLabel}>{sendLabel}</button>
    </div>
  );
}
