function resolveLabel(label) {
  if (!label) return "";
  if (typeof label === "string") return label;
  if (typeof label === "object") {
    return label.es || label.en || label.pt || label.ca || Object.values(label)[0] || "";
  }
  return String(label);
}

export default function ChatOptions({ options, onSelect }) {
  return (
    <div className="options-container">
      {options.map((opt) => (
        <span
          key={opt.id}
          className="option-chip"
          onClick={() => onSelect(opt)}
        >
          {resolveLabel(opt.label)}
        </span>
      ))}
    </div>
  );
}
