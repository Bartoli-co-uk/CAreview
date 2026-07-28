import { useState } from "react";
import { InfoIcon } from "./icons";

// Small hover/focus tooltip used to explain jargon (e.g. "report-only") to
// non-technical readers without cluttering the main copy.
export function InfoTooltip({ text }: { text: string }) {
  const [open, setOpen] = useState(false);
  return (
    <span
      className="tooltip-wrap"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <button
        type="button"
        className="tooltip-icon"
        style={{ background: "none", border: "none", padding: 0, display: "flex" }}
        aria-label={text}
      >
        <InfoIcon width={14} height={14} />
      </button>
      {open && <span className="tooltip-bubble">{text}</span>}
    </span>
  );
}
