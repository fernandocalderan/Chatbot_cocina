function ChatHeader({ title, subtitle, status, logoUrl }) {
  return (
    <header className="chat-header">
      <div className="header-text">
        <div className="chat-header-row">
          {logoUrl && <img src={logoUrl} alt="Logo" className="chat-logo" />}
          <p className="chat-title">{title}</p>
        </div>
        {subtitle && <p className="chat-subtitle">{subtitle}</p>}
      </div>
      {status?.label && <span className="chat-status-label">{status.label}</span>}
    </header>
  );
}

export default ChatHeader;
