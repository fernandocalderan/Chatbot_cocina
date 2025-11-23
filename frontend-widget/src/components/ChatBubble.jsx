export default function ChatBubble({ role, text }) {
  return (
    <div className={`bubble ${role}`}>
      {text}
    </div>
  );
}
