# [Claude/Codex] security review: [milestone/project]

**Outcome:** `[PASS / PASS_WITH_NOTES / REMEDIATION_REQUIRED / BLOCKED / INCONCLUSIVE]`
**Reviewer role:** `[Claude security reviewer / Codex security reviewer]`
**Provider/model:** `[provider and model if known]`
**Fresh session/task ID:** `[identifier]`
**Candidate SHA:** `[full SHA]`
**Tree identity:** `[digest or description]`
**Threat model:** `[path and version]`
**Created at:** `[UTC timestamp]`
**Peer conclusion withheld:** `yes`

## Scope and evidence

- Requirements and roadmap: `[paths/versions]`
- Changed attack surface: `[summary]`
- Tests/scanners reviewed: `[evidence]`
- Unavailable or failed evidence: `[list]`
- Network/tool limits: `[limits]`

## Coverage

| Area | Evidence considered | Result/gap |
|---|---|---|
| Threats and abuse cases | `[evidence]` | `[result]` |
| Authentication/authorization/privilege | `[evidence]` | `[result]` |
| Secrets/logs/data exposure | `[evidence]` | `[result]` |
| Inputs/injection/deserialization/paths/commands | `[evidence]` | `[result]` |
| Dependencies/build/release/CI supply chain | `[evidence]` | `[result]` |
| Network/external integrations | `[evidence]` | `[result]` |
| Configuration/unsafe defaults | `[evidence]` | `[result]` |
| Privacy/retention/migration/deletion | `[evidence]` | `[result]` |
| Governance/session/review integrity | `[evidence]` | `[result]` |

## Findings

### [SEC-ID]: [title]

- Fingerprint: `[stable fingerprint]`
- Category/reference: `[category, CWE or standard where useful]`
- Severity: `[critical/high/medium/low/info]`
- Confidence: `[high/medium/low]`
- Blocking: `[yes/no]`
- Affected location: `[path:line]`
- Evidence: `[evidence]`
- Attack preconditions: `[preconditions]`
- Impact: `[impact]`
- Exploitability: `[assessment]`
- Recommended remediation: `[change]`
- Verification method: `[method]`
- Disposition: `[open/closed/risk-candidate]`

## Conclusion and limitations

[State only what the scope and evidence support. Missing or failed evidence is INCONCLUSIVE. Critical/high findings always block. Do not claim the project is secure or certified.]

Any repair that creates a new milestone candidate invalidates both general and
both security reports; rerun all four against the one new SHA.
The milestone workflow permits at most two security-remediation cycles and an
absolute maximum of five iterations for any loop. Exhaustion blocks for the
human.
