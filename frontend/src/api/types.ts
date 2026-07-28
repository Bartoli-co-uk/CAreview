// Types mirror the exact JSON shapes CAreview's stdlib backend returns.
// See graph.normalize_policy (graph.py) and analyzer.analyze (analyzer.py).

export type PolicyState = "enabled" | "disabled" | "enabledForReportingButNotEnforced";

export interface PolicyConditions {
  includeUsers: string[];
  excludeUsers: string[];
  includeGroups: string[];
  excludeGroups: string[];
  includeRoles: string[];
  excludeRoles: string[];
  includeApplications: string[];
  excludeApplications: string[];
  clientAppTypes: string[];
  includePlatforms: string[];
  excludePlatforms: string[];
  includeLocations: string[];
  excludeLocations: string[];
  signInRiskLevels: string[];
  userRiskLevels: string[];
}

export interface GrantControls {
  operator: string;
  builtInControls: string[];
}

export interface Policy {
  id: string;
  displayName: string;
  state: PolicyState;
  conditions: PolicyConditions;
  grantControls: GrantControls;
  sessionControls: string[];
}

export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface Finding {
  id: string;
  title: string;
  severity: Severity;
  weight: number;
  rationale: string;
  remediation: string;
  affectedPolicies: string[];
}

export type RuleStatus = "pass" | "fail" | "not_evaluable";

export interface EvaluatedRule {
  id: string;
  title: string;
  status: RuleStatus;
}

export interface Analysis {
  score: number;
  scoreIsHeuristic: boolean;
  policyCount: number;
  findings: Finding[];
  evaluated: EvaluatedRule[];
  notEvaluable: string[];
}

export interface PoliciesResponse {
  policies: Policy[];
  count: number;
}

export type ApiErrorCode = "not_authenticated" | "consent_required" | "graph_error" | "invalid_url";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; status: number; error: ApiErrorCode | "network_error" | "unknown_error"; message?: string };

export interface AuthStartResponse {
  handle: string;
  user_code: string;
  verification_uri: string;
  expires_in: number;
  interval: number;
}

export type AuthPollState = "pending" | "success" | "expired" | "error";

export interface AuthPollResponse {
  state: AuthPollState;
  error?: string;
}

export interface AuthAppOnlyResponse {
  state: "success";
}

export type AuthErrorResponse = { state: "error"; error: string };
