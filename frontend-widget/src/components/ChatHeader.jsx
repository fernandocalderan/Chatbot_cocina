function ChatHeader({ title, subtitle, status }) {
  return (
    <header className="chat-header">
      <div className="header-text">
        <p className="chat-title">{title}</p>
        {subtitle && <p className="chat-subtitle">{subtitle}</p>}
      </div>
      {status?.label && <span className="chat-status-label">{status.label}</span>}
    </header>
  );
}

export default ChatHeader;
