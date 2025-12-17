function resolveLabel(label) {
  if (!label) return "";
  if (typeof label === "string") return label;
  if (typeof label === "object") {
    return label.es || label.en || label.pt || label.ca || Object.values(label)[0] || "";
  }
  return String(label);
}

export default function ChatOptions({ options, onSelect }) {
  const normalized = Array.isArray(options) ? options : [];
  return (
    <div className="options-container">
      {normalized.map((opt) => (
        <span
          key={typeof opt === "string" ? opt : opt.id}
          className="option-chip"
          onClick={() => onSelect(opt)}
        >
          {resolveLabel(typeof opt === "string" ? opt : opt.label)}
        </span>
      ))}
    </div>
  );
}
