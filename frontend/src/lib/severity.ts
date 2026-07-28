import type { Severity } from "../api/types";

export interface SeverityInfo {
  label: string;
  color: string;
  order: number;
}

// Single source of truth for severity display, mirroring analyzer.py's
// _SEVERITY_ORDER and web/app.js's SEVERITY_LABEL. Unknown severities fall
// back to a neutral, still-legible presentation rather than throwing.
const SEVERITY_MAP: Record<Severity, SeverityInfo> = {
  critical: { label: "Critical", color: "#b42318", order: 0 },
  high: { label: "High", color: "#d92d20", order: 1 },
  medium: { label: "Medium", color: "#b54708", order: 2 },
  low: { label: "Low", color: "#3538cd", order: 3 },
  info: { label: "Info", color: "#475467", order: 4 },
};

const FALLBACK: SeverityInfo = { label: "Unknown", color: "#667085", order: 99 };

export function severityInfo(severity: string): SeverityInfo {
  return SEVERITY_MAP[severity as Severity] ?? { ...FALLBACK, label: severity || FALLBACK.label };
}

export function sortBySeverity<T extends { severity: string }>(items: T[]): T[] {
  return [...items].sort((a, b) => severityInfo(a.severity).order - severityInfo(b.severity).order);
}

export interface ScoreBand {
  label: string;
  color: string;
}

// Thresholds mirror the informal "Good/Needs improvement/Poor" bands the
// reviewed mockup uses; boundaries are inclusive on the lower bound.
export function scoreBand(score: number): ScoreBand {
  if (score >= 80) return { label: "Good", color: "#079455" };
  if (score >= 50) return { label: "Needs improvement", color: "#dc6803" };
  return { label: "Poor", color: "#d92d20" };
}
