import type { Policy } from "../api/types";

// Mirrors rules.py's ADMIN_ROLE_TEMPLATE_IDS. Duplicated client-side since
// there is no API metadata exposing this set today; keep in sync with
// rules.py if it changes.
export const ADMIN_ROLE_TEMPLATE_IDS: ReadonlySet<string> = new Set([
  "62e90394-69f5-4237-9190-012177145e10", // Global Administrator
  "e8611ab8-c189-46e8-94e1-60213ab1f814", // Privileged Role Administrator
  "7be44c8a-adaf-4e2a-84d6-ab2649e08a13", // Privileged Authentication Administrator
  "194ae4cb-b126-40b2-bd5b-6091b380977d", // Security Administrator
  "29232cdf-9323-42fd-ade2-1d097af3e4de", // Conditional Access Administrator
  "f28a1f50-f6e7-4571-818b-6a12f2af6b6c", // Exchange Administrator
  "158c047a-c907-4556-b7ef-446551a6b5f7", // SharePoint Administrator
  "966707d0-3269-4727-9be2-8c3a10f19b9d", // Helpdesk Administrator
  "b0f54661-2d74-4c50-afa3-1ec803f12efe", // Authentication Administrator
]);

export interface PolicyCounts {
  total: number;
  enabled: number;
  reportOnly: number;
  disabled: number;
}

export function countByState(policies: Policy[]): PolicyCounts {
  const counts: PolicyCounts = { total: policies.length, enabled: 0, reportOnly: 0, disabled: 0 };
  for (const policy of policies) {
    if (policy.state === "enabled") counts.enabled += 1;
    else if (policy.state === "enabledForReportingButNotEnforced") counts.reportOnly += 1;
    else counts.disabled += 1;
  }
  return counts;
}

export interface GlanceCounts {
  userBased: number;
  groupBased: number;
  cloudAppPolicies: number;
  authStrength: number; // policies requiring MFA
  deviceCompliance: number;
  adminTargeted: number;
}

export function glanceCounts(policies: Policy[]): GlanceCounts {
  let userBased = 0;
  let groupBased = 0;
  let cloudAppPolicies = 0;
  let authStrength = 0;
  let deviceCompliance = 0;
  let adminTargeted = 0;
  for (const policy of policies) {
    const c = policy.conditions;
    if (c.includeUsers.length) userBased += 1;
    if (c.includeGroups.length) groupBased += 1;
    if (c.includeApplications.length) cloudAppPolicies += 1;
    if (policy.grantControls.builtInControls.includes("mfa")) authStrength += 1;
    if (
      policy.grantControls.builtInControls.includes("compliantDevice") ||
      policy.grantControls.builtInControls.includes("domainJoinedDevice")
    ) {
      deviceCompliance += 1;
    }
    if (c.includeRoles.some((role) => ADMIN_ROLE_TEMPLATE_IDS.has(role))) adminTargeted += 1;
  }
  return { userBased, groupBased, cloudAppPolicies, authStrength, deviceCompliance, adminTargeted };
}

export interface CoveragePercent {
  mfaCoveragePct: number;
  deviceComplianceCoveragePct: number;
}

export function coveragePercent(policies: Policy[]): CoveragePercent {
  const enabled = policies.filter((p) => p.state !== "disabled");
  const denom = enabled.length || 1;
  const mfa = enabled.filter((p) => p.grantControls.builtInControls.includes("mfa")).length;
  const device = enabled.filter(
    (p) =>
      p.grantControls.builtInControls.includes("compliantDevice") ||
      p.grantControls.builtInControls.includes("domainJoinedDevice"),
  ).length;
  return {
    mfaCoveragePct: policies.length ? Math.round((mfa / denom) * 100) : 0,
    deviceComplianceCoveragePct: policies.length ? Math.round((device / denom) * 100) : 0,
  };
}

export function tallyBy<T extends string>(values: T[]): Record<string, number> {
  const tally: Record<string, number> = {};
  for (const value of values) tally[value] = (tally[value] ?? 0) + 1;
  return tally;
}

export function clientAppTypeTally(policies: Policy[]): Record<string, number> {
  return tallyBy(policies.flatMap((p) => p.conditions.clientAppTypes));
}

// Best-effort, human-facing label for a policy's primary control, derived
// from grantControls/sessionControls — there is no dedicated "type" field on
// the wire.
export function derivedPolicyType(policy: Policy): string {
  const controls = policy.grantControls.builtInControls;
  if (controls.includes("block")) return "Block";
  if (controls.includes("mfa")) return "MFA";
  if (controls.includes("compliantDevice") || controls.includes("domainJoinedDevice")) return "Device compliance";
  if (policy.sessionControls.length) return "Session control";
  if (policy.conditions.includeRoles.length) return "Role-based";
  if (policy.conditions.includeGroups.length) return "Group-based";
  if (policy.conditions.clientAppTypes.length) return "Client app";
  return "User-based";
}
