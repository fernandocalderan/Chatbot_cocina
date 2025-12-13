import { QUOTA_COPY } from "../constants/quota";
import "../styles/chat.css";

export default function QuotaBanner({ status, savingMode, needsUpgrade, upgradeUrl }) {
  const normalized = (status || "ACTIVE").toUpperCase();
  if (normalized === "ACTIVE") return null;

  const isSaving = savingMode || normalized === "SAVING";
  const isLocked = normalized === "LOCKED";
  const copy = isLocked ? QUOTA_COPY.LOCKED : QUOTA_COPY.SAVING;

  return (
    <div className={`quota-banner ${isLocked ? "locked" : "saving"}`}>
      <div>
        <strong className="quota-title">{copy.title}</strong>
        <p className="quota-text">{copy.message}</p>
      </div>
      {needsUpgrade && (
        <button
          className="quota-cta"
          type="button"
          onClick={() => {
            if (upgradeUrl) window.open(upgradeUrl, "_blank", "noopener");
          }}
        >
          {copy.cta}
        </button>
      )}
    </div>
  );
}
