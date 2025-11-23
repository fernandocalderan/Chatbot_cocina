export default function ChatOptions({ options, onSelect }) {
  return (
    <div className="options-container">
      {options.map((opt) => (
        <span
          key={opt.id}
          className="option-chip"
          onClick={() => onSelect(opt)}
        >
          {opt.label}
        </span>
      ))}
    </div>
  );
}
