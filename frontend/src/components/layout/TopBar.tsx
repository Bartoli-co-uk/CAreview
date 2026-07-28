import type { ReactNode } from "react";
import { CalendarIcon } from "../icons";

interface TopBarProps {
  title: string;
  subtitle?: string;
  lastRefreshed: Date | null;
  actions?: ReactNode;
}

export function TopBar({ title, subtitle, lastRefreshed, actions }: TopBarProps) {
  return (
    <div className="topbar">
      <div>
        <h2>{title}</h2>
        {subtitle && <p className="subtitle">{subtitle}</p>}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        {lastRefreshed && (
          <span className="badge" style={{ background: "#f2f4f7", color: "#475467" }}>
            <CalendarIcon width={14} height={14} />
            Refreshed {lastRefreshed.toLocaleTimeString()}
          </span>
        )}
        {actions}
      </div>
    </div>
  );
}
