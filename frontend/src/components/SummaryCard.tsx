import type { ReactNode } from "react";

interface SummaryCardProps {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export function SummaryCard({ icon, title, children, footer }: SummaryCardProps) {
  return (
    <div className="card">
      <div className="card-header-title" style={{ marginBottom: 12 }}>
        {icon}
        <span>{title}</span>
      </div>
      {children}
      {footer && <div style={{ marginTop: 12 }}>{footer}</div>}
    </div>
  );
}
