import type { ReactNode } from "react";
import { AlertTriangleIcon } from "../components/icons";

interface PlaceholderProps {
  icon?: ReactNode;
  title: string;
  description: string;
}

// A clearly-labeled "not available yet" placeholder for sections that have
// no backing data today (Reports, Audit Log) — set expectations honestly for
// both technicians and management rather than showing fabricated data.
export function Placeholder({ icon, title, description }: PlaceholderProps) {
  return (
    <div className="card placeholder-card">
      {icon ?? <AlertTriangleIcon width={32} height={32} />}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}
