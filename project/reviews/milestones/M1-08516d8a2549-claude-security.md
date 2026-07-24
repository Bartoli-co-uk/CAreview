# Claude security review: M1 (MVP Conditional Access analyzer)

**Outcome:** `PASS_WITH_NOTES`
**Reviewer role:** Claude security reviewer
**Provider/model:** Claude (Opus 4.8), this session
**Fresh session/task ID:** milestone-M1-security (same session as the implementation — see Limitations)
**Candidate SHA:** `08516d8a2549e0aeb23c54a1d87f2061fd47babf`
**Tree identity:** working tree clean at freeze
**Threat model:** local single-user tool; trust boundaries are local-browser ↔
loopback-server ↔ Microsoft (identity + Graph) over TLS; see
`docs/security-boundaries.md` and the "CAreview application boundaries" section
added for this project
**Created at:** 2026-07-24T16:XX:XXZ
**Peer conclusion withheld:** yes (written before invoking the Codex milestone-security review)

## Scope and evidence

- Requirements and roadmap: `project/brief/PROJECT_BRIEF.md` v1 (Data and
  security section), `ROADMAP.md` v3 (architecture/security assumptions, RISK-001..004)
- Changed attack surface: local HTTP server (`server.py`), device-code auth
  (`auth.py`), Graph client (`graph.py`), analyzer (`analyzer.py`/`rules.py`),
  browser UI (`web/*`)
- Tests/scanners reviewed: `tests/test_server.py`, `tests/test_auth.py`,
  `tests/test_graph.py`, `tests/test_ui_safety.py` (79 of 80 total tests touch
  security-relevant paths); no external SAST/dependency scanner is configured
  (project has zero third-party dependencies, so a dependency scanner would have
  no surface to scan)
- Unavailable or failed evidence: live-tenant sign-in/fetch not performed
  (protected action; human access restrictions); in-browser DOM confirmation not
  performed (no browser tool available this session)
- Network/tool limits: none beyond the above; static source review + test
  execution only

## Coverage

| Area | Evidence considered | Result/gap |
|---|---|---|
| Threats and abuse cases | Loopback exposure, DNS rebinding, CSRF, token theft, SSRF via Graph paging, XSS via tenant-controlled strings | Addressed for each identified abuse case (see findings/notes); no unaddressed case found |
| Authentication/authorization/privilege | Device-code flow against a Microsoft first-party public client; no client secret; least-privilege delegated scopes (`Policy.Read.All`, `Application.Read.All`, `Directory.Read.All`); no app-level authz beyond the loopback/Origin gate | Consistent with the approved, human-decided model (`DECISION-001`); RISK-002 (no additional local auth) is a documented, accepted residual, not an oversight |
| Secrets/logs/data exposure | `grep` for `print`/`logging` calls in `server.py`/`auth.py`/`graph.py`/`analyzer.py`/`rules.py`: only two `print()` calls, both startup/shutdown banners with no tenant data or tokens; `log_message` overridden to silence default HTTP access logging | No token, tenant data, or secret is logged anywhere in product code |
| Inputs/injection/deserialization/paths/commands | No `subprocess`/`eval`/`exec`/`os.system` anywhere in product code; static file serving is allowlisted plus a `WEB_ROOT` containment check; JSON bodies are size-bounded (`MAX_BODY_BYTES`) and type-checked before use; `graph.normalize_policy` defensively coerces every nested field (`_as_dict`) so a malformed/attacker-influenced Graph response cannot crash or type-confuse the analyzer | No injection or deserialization vector found |
| Dependencies/build/release/CI supply chain | Zero third-party Python packages (stdlib only); `.github/workflows/validate.yml`'s only action is pinned to a full commit SHA (`actions/checkout@11d5960a...`) | Supply-chain surface is minimal by design; nothing to remediate |
| Network/external integrations | Egress is limited to `login.microsoftonline.com` (auth.py, tenant regex-validated against injection into the authority URL) and `graph.microsoft.com` (`graph.is_graph_url` requires exact scheme+host+no-embedded-credentials before every request, including every `@odata.nextLink` page, and HTTP redirects are refused by a custom `_NoRedirect` handler) | Both identified SSRF/token-exfiltration vectors (arbitrary next-link host; redirect-based token leak) are closed with tests proving it (`test_non_graph_next_link_rejected_without_sending_token`) |
| Configuration/unsafe defaults | Server binds only to an explicit loopback allowlist (`_LOOPBACK_BIND_ADDRESSES`); `build_server` raises on any other address; Host-header allowlist defends against DNS rebinding; Origin check on all state-changing (`POST`) endpoints defends against CSRF; sensitive `GET` responses (`/api/policies`, `/api/analysis`) set `Cache-Control: no-store` | Defaults are conservative; no unsafe default identified |
| Privacy/retention/migration/deletion | Tokens and break-glass IDs held only in process memory (`auth.AuthManager`, `server._break_glass_ids`), cleared on logout/new sign-in via a concurrency-safe generation guard; no persistence layer exists to migrate or delete from | Consistent with the "local only, no persistence" design goal; RISK-002's residual (another local process reading loopback traffic) is named, not hidden |
| Governance/session/review integrity | Every merged issue has a committed Codex report bound to an exact SHA (`project/reviews/issues/`), a documented gate-policy decision for the sandbox's execution-evidence limitation (`DECISION-004`), and explicit human decisions for every repair-budget exception (`DECISION-006`..`010`) | Full paper trail exists for every candidate that reached `main`; no undocumented shortcut found |

## Findings

### SEC-001: Local loopback API has no authentication of its own (accepted, pre-existing)

- Fingerprint: `careview-loopback-no-authn-2026-07`
- Category/reference: CWE-306 (Missing Authentication for Critical Function), scoped to a local-only trust model
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Affected location: `server.py` (all `/api/*` routes)
- Evidence: no bearer/session cookie/local secret gate protects the local API
  beyond the Host allowlist and Origin check; any process on the same machine,
  running as the same OS user (or one that can reach `127.0.0.1` under a shared
  account), could call `/api/policies`/`/api/analysis` while a token is live.
- Attack preconditions: attacker already has local code execution as the same
  user (or a shared-account/multi-user host) — a materially different, and
  already much higher, bar than a remote attacker.
- Impact: local disclosure of the signed-in user's Conditional Access policies
  and score/findings while a session is active; no token is disclosed (Graph
  tokens are held server-side, never returned to the browser).
- Exploitability: requires existing local code execution; this is not remotely
  exploitable given the Host/Origin/no-redirect/DNS-rebinding defenses already
  in place.
- Recommended remediation: none required for the MVP's stated single-user
  local-tool scope. If CAreview is ever run on a shared or multi-user host, add
  a per-run local token/PIN gate (already discussed and consciously deferred:
  `DECISION-001`, `RISK-002`).
- Verification method: re-review if the deployment model changes from
  single-user-local.
- Disposition: `risk-candidate` (already accepted by the human via `DECISION-001`; carried forward here for milestone-level visibility, not newly discovered)

## Conclusion and limitations

No critical or high-severity finding exists in this candidate. The one
finding recorded (SEC-001) is a previously identified and human-accepted
residual risk (RISK-002), re-surfaced here at the milestone level rather than
newly discovered — I found no additional issue beyond what the per-issue
security-relevant Codex findings already caught and this project's records
already disclose (token-exfiltration/SSRF in `graph.py`, concurrency races in
`auth.py`/`web/app.js`, all fixed and tested before merge).

This review passed within the scope and evidence documented above. It is not a
penetration test, a certification, or proof that no other vulnerability exists.

**Limitation on independence:** this review was written within the same
overall session that authored the implementation, not a fully separate
top-level task with no shared context, so it cannot claim the same
independence as a genuinely fresh reviewer. I mitigated this by re-reading the
final source fresh, grepping for concrete evidence (logging, injection sinks,
secrets, CI pinning) rather than relying on recollection, and by checking every
finding against the committed record rather than my own prior reasoning. The
**Codex security review**, run as a separate ephemeral process with no access
to this report, is the reviewer that genuinely satisfies this workflow's
independence requirement; the human should weight that report — and their own
judgment — more heavily than this one where they differ.

Any repair that creates a new milestone candidate invalidates both general and
both security reports; rerun all four against the one new SHA.
