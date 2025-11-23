import ChatBubble from "./ChatBubble";

export default function ChatMessages({ messages }) {
  return (
    <div className="chat-messages">
      {messages.map((msg, i) => (
        <ChatBubble key={i} role={msg.role} text={msg.text} />
      ))}
    </div>
  );
}
