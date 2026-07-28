import { Placeholder } from "./Placeholder";

export function AuditLog() {
  return (
    <Placeholder
      title="Audit Log — not available yet"
      description="CAreview persists no tenant activity by design — it holds nothing on disk between runs, so there is no
        local audit trail to show. See the README's Security model for details."
    />
  );
}
