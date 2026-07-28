# Claude security review: milestone M2 (dual-mode authentication)

**Outcome:** `PASS_WITH_NOTES`
**Reviewer role:** `Claude security reviewer`
**Provider/model:** `Anthropic — Claude Opus 5 (claude-opus-5), read-only reviewer task`
**Fresh session/task ID:** `fresh ephemeral reviewer task; no provider-side task identifier is exposed to the reviewer (recorded as unavailable rather than invented)`
**Candidate SHA:** `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`
**Tree identity:** root tree `2e1bd6e8bb9fca4e0eaad7f28a5450e6c1c96bd3`; reviewed blobs — `auth.py` `6362fff52c2276ff2e14b270aef536f1de4695b2`, `server.py` `3e7baad12ecfe0879c484b2a9d5853bef749a8f6`, `web/app.js` `64c6128bfc519541bde76677dc09ceac630e0f41`, `web/index.html` `920349d8882bcea23044a43d73325e2caf9840b8`. `git rev-parse HEAD` = the candidate SHA; branch `main`, ahead of `origin/main` by 2. Working tree contains no modified tracked files, but one untracked in-flight peer report file (see SEC-006)
**Threat model:** `docs/security-boundaries.md` at this commit (CAreview application boundaries, incl. the M2 `DECISION-014` trust-boundary delta); `ROADMAP.md` v4 Risks and decisions table (`RISK-001`..`RISK-008`)
**Created at:** `2026-07-28T07:13:22Z`
**Peer conclusion withheld:** `yes`

## Scope and evidence

- Requirements and roadmap: `ROADMAP.md` v4 (approved `DECISION-015`, binds `9e5ba6d`), M2 row and issue rows 7–11; `project/brief/PROJECT_BRIEF.md` v2 (approved `DECISION-013`); `project/decisions/DECISION-014-app-only-secret-retention-and-risk002.md`; `project/milestones/M2.md` (`Status: REVIEWING`); `project/issues/ISSUE-0007.md`..`ISSUE-0011.md` (all `COMPLETE`); `project/status/CURRENT.md` (stage `MILESTONE_REVIEW`, active milestone `M2`, next permitted action = run the four blind reviews against the frozen candidate).
- Reviewed source at the candidate: `auth.py` (447 lines — device-code flow, `build_client_credentials_request`, `start_app_only`, `_renew_app_only`, `get_token`, `logout`, `_classify_app_only_error`, `_app_only_authority`), `server.py` (416 lines — `/api/auth/app` and its validators, Host/Origin gates, `_send_json`/`_reject`, `log_message` suppression), `web/app.js` (396 lines — `submitAppOnly`, `clearAppOnlySecretField`, mode switches, `signOut`), `web/index.html` (app-only form markup, CSP meta), `graph.py` (egress pinning, for comparison), `tests/test_auth.py`, `tests/test_server.py`, `tests/test_ui_safety.py`.
- Changed attack surface vs. M1 (`git diff 6311a11a..HEAD -- '*.py' web/`): `auth.py` +215/−, `server.py` +73, `web/app.js` +92, `web/index.html` +49, `web/style.css` +25, tests +966. No new files, no new imports beyond the stdlib set already present (`json`, `re`, `secrets`, `threading`, `time`, `urllib.*`), no `requirements.txt`/`package.json`/`pyproject.toml`/lockfile anywhere in the tree. The single new externally reachable entry point is `POST /api/auth/app`.
- Checks I re-ran myself against this exact SHA (not relied on from the record):
  - `python3 -m unittest discover -s tests` → `Ran 173 tests ... OK`, exit 0.
  - `python3 -m py_compile $(git ls-files '*.py')` → exit 0.
  - `python3 scripts/validate_repo.py` → "Repository validation passed (67 required files checked)", exit 0 (with a NOTICE that the PowerShell syntax check was skipped because `pwsh` is unavailable locally; CI runs it).
  - Targeted dynamic probes I wrote and ran against the candidate `auth.py` (mock transport, injected clock) to test renewal behaviour and `repr()` leakage — see SEC-001.
  - CPython 3.14.6 `urllib.request.HTTPRedirectHandler.redirect_request` source inspected directly to establish redirect semantics for the token POST — see SEC-002.
- Tests/scanners reviewed: `tests/test_auth.py::AppOnlySecretLeakTests` (secret absent from return value, `repr()`, exception message in literal / URL-encoded / JSON-escaped forms, `logging` output, stderr); `tests/test_server.py::test_secret_absent_from_every_response_body` (validation rejections, malformed-body path, success, every surfaced `AuthError` label, all three encodings), `test_silent_renewal_failure_surfaces_stable_non_secret_non_5xx_error`, `test_logout_clears_app_only_state`, `test_nothing_logged_to_stderr`, tenant/client_id/secret boundary tests; `tests/test_ui_safety.py::AppOnlyModeToggleTests` (password type, `autocomplete="off"`, clearing on submit/`finally`/mode switch/logout, absence of `console.`/`localStorage`/`sessionStorage`/`document.cookie`, secret not concatenated into a URL, CSP meta unchanged).
- Unavailable or failed evidence: no live Entra tenant and no real client secret (a protected action, correctly not performed); no browser or DOM automation available, so all browser-side secret handling is verified statically plus by a human-performed manual walkthrough recorded in `project/handoffs/ISSUE-0010-handoff.md`, which I can read but cannot independently reproduce; no process-memory, core-dump, or swap inspection performed; no dependency/SCA scanner run (nothing to scan — stdlib only); `pwsh` unavailable locally.
- Network/tool limits: this review made no network requests. All auth behaviour was exercised through injected mock transports.

## Coverage

| Area | Evidence considered | Result/gap |
|---|---|---|
| Threats and abuse cases | `docs/security-boundaries.md` "CAreview application boundaries"; `ROADMAP.md` v4 `RISK-002` (widened), `RISK-005`, `RISK-006`; `DECISION-014`; `server.py:289-372` | Boundary delta is accurately documented and matches the code. One abuse case reachable through the new endpoint is not explicitly enumerated in `RISK-002`/`DECISION-014` — SEC-003 |
| Authentication/authorization/privilege | `auth.py:239-447`; `server.py:216-372`; `SCOPES` (`auth.py:55`), `APP_ONLY_SCOPE` (`auth.py:62`); `tests/test_auth.py`, `tests/test_server.py` | Device-code path unchanged in behaviour except the M1→M2 scope trim to `Policy.Read.All` alone; app-only is opt-in and cannot override its scope (no caller-supplied scope parameter). Single-concurrency and generation-counter guards are present on both flows and stale-response races are tested. `.default` over-privilege is `RISK-006`, correctly recorded as accepted-not-mitigated |
| Secrets/logs/data exposure | `auth.py:82-101,350-420`; `server.py:184-194,347-377`; `web/app.js:145-212`; `web/index.html` app-only form; leak test suites in all three test files; my own `repr(AuthManager)` probe | No path found by which the secret reaches disk, a tracked file, a log record, stderr, a response body, a returned value, a raised exception, `repr()`, `console`, web storage, a cookie, or a URL. `_classify_app_only_error` never echoes provider text — a strong, correctly-motivated control. Residual, non-remediable in-process exposure noted as SEC-005 |
| Inputs/injection/deserialization/paths/commands | `server.py:115-154,347-361`; `auth.py:103-142`; `server.py:273-287` (`MAX_BODY_BYTES` 64 KiB) | Tenant/client_id/secret are type-, format-, and length-checked before any retention or outbound call, mirrored (not replaced) by `auth.py`'s own checks. Tenant regex admits only a GUID or DNS-style labels, so it cannot alter the authority host or inject a path/query. All values are `urlencode`d into the body. No `subprocess`, `os.system`, `eval`, `pickle`, or filesystem write anywhere in the M2 diff; static serving is allowlist + `resolve()`-confined (unchanged from M1). No path/command surface introduced by M2 |
| Dependencies/build/release/CI supply chain | `git diff 6311a11a..HEAD` import survey; absence of any manifest/lockfile; `.github/workflows/validate.yml` diff | No new dependency of any kind; stdlib only, constraint upheld. The only CI change adds `py_compile` and `unittest` steps; `actions/checkout` remains SHA-pinned with `persist-credentials: false`; no secrets, no `pull_request_target`, no fork-triggered privileged job |
| Network/external integrations | `auth.py:103-189`, `graph.py:25-97` | App-only token requests go only to `https://login.microsoftonline.com/<validated-tenant>/oauth2/v2.0/token`; Graph egress is host-pinned to `graph.microsoft.com` with an explicit no-redirect opener. The token endpoint lacks the equivalent redirect suppression — SEC-002 |
| Configuration/unsafe defaults | `server.py:52-54,380-399`; `web/index.html:6-7`; `server.py:164-173` | Default remains device-code; app-only is hidden until explicitly chosen. Loopback bind is enforced by the factory (`ValueError` on non-loopback); Host allowlist on all requests and Origin check on all POSTs; CSP both as a header and a meta tag with `form-action 'none'`, `frame-ancestors 'none'`, plus `nosniff`. `CAREVIEW_PORT` is the only env input and cannot change the bind host. One header omission — SEC-004 |
| Privacy/retention/migration/deletion | `auth.py:239-254,338-347,350-420`; `web/app.js:113-127,145-161,195-200`; `DECISION-014` | Secret acquisition → transit → retention → clearing is implemented as documented: cleared on `logout()`, on supersession by either sign-in mode, and by process exit; browser field cleared in a `finally` on submit, on both mode-switch directions, and on logout. No persistence anywhere. One lifecycle case leaves the secret retained while the UI reports signed-out — SEC-001 |
| Governance/session/review integrity | `project/status/CURRENT.md`; `project/milestones/M2.md`; `git log`, `git diff --stat 98be0bc..HEAD` | The candidate I was asked to review (`9c01749`) is not the SHA `project/status/CURRENT.md` names as frozen (`98be0bc`). I verified independently that `98be0bc..9c01749` touches only `project/` governance files, so the product tree under review is byte-identical to the frozen product content and this is not a wrong-target review. Record accuracy noted as SEC-006. Peer conclusions were not consulted: I did not open anything under `project/reviews/milestones/` |

## Findings

No critical or high findings. Nothing below blocks the milestone; SEC-001 and SEC-003 warrant an explicit human decision at acceptance.

### SEC-001: App-only renewal retries the retained secret without bound, and keeps it after permanent failure while the UI reports signed-out

- Fingerprint: `careview/m2/auth/app-only-renewal-unbounded-retry-and-retention`
- Category/reference: CWE-307 (improper restriction of excessive authentication attempts); CWE-459 (incomplete cleanup); secondary CWE-772
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Affected location: `auth.py:389-444` (`_renew_app_only`, `get_token`); reached from `server.py:236,255` on every `/api/policies` and `/api/analysis` request
- Evidence: `_renew_app_only` has no failure counter, backoff, or cooldown, and on failure clears only `_access_token`/`_token_expires_at` (`auth.py:410-413`) — never `_app_only_secret`. `get_token()` therefore re-enters renewal on every call once the token has expired. I ran the candidate `auth.py` directly with a mock transport whose first call succeeds and all later calls return `400 invalid_client`, then advanced the injected clock past expiry and called `get_token()` six times: the transport recorded **7 total outbound calls** (initial + one per `get_token()`), each carrying the retained secret in its body to `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token`, each returning `None`, and `mgr._app_only_secret is not None` remained `True` throughout. The same probe confirmed `repr(mgr)` is the default `<auth.AuthManager object at 0x…>` with no secret (consistent with `tests/test_auth.py::test_secret_absent_from_manager_repr`). `web/app.js:355-385` (`loadLiveAnalysis`) issues `/api/policies` and `/api/analysis` in parallel, so each UI refresh triggers two attempts. `tests/test_server.py::test_silent_renewal_failure_surfaces_stable_non_secret_non_5xx_error` covers the *response* correctness of this path but asserts nothing about attempt count or post-failure retention.
- Attack preconditions: none in the adversarial sense — this is reached by the ordinary operational case of a rotated, revoked, or expired client secret, or a sustained network/identity outage, while an app-only session is open. An attacker with local access can additionally drive the attempt rate by polling `/api/policies`.
- Impact: (a) an invalid client secret is re-transmitted to Microsoft indefinitely and at UI-driven frequency, generating repeated `invalid_client` sign-in failures against the app registration, which is noisy in the tenant's sign-in logs and may attract identity-protection throttling; (b) the retained secret's in-memory lifetime is decoupled from the user-visible session — the UI shows "sign in to see your tenant's analysis" (`web/app.js:365-367`) while the live secret is still held, so a user who believes the session has ended has no indication that only an explicit **Sign out** or process exit clears it. `docs/security-boundaries.md:112-115` and `DECISION-014` describe the retention window as the "app-only session", which this case stretches past any user-perceptible session boundary without saying so.
- Exploitability: low as an attack (requires local code execution, which already grants more direct access to the same process memory); moderate as a likely-to-occur operational condition, since secret rotation is exactly the practice `README.md` recommends.
- Recommended remediation: on a non-transient renewal failure (in particular an HTTP 400/401 provider rejection, as distinct from `network_error`), clear `_app_only_tenant`/`_app_only_client_id`/`_app_only_secret` so the credential is dropped rather than replayed, and require re-entry; and/or add a small failure counter plus a minimum interval between renewal attempts. Whichever is chosen, align `docs/security-boundaries.md` and `README.md` with the actual clearing conditions.
- Verification method: extend `tests/test_auth.py` with a mock-transport test that asserts (1) at most N outbound calls after M `get_token()` calls following a hard renewal rejection, and (2) `_app_only_secret is None` after a terminal rejection; re-run `python3 -m unittest discover -s tests`.
- Disposition: `open` (fix or an explicit, time-bounded human acceptance recorded at M2 acceptance)

### SEC-002: The token endpoint's transport follows HTTP redirects and does not pin the responding host, unlike the Graph client

- Fingerprint: `careview/m2/auth/token-transport-follows-redirects-unpinned`
- Category/reference: CWE-601 / CWE-918 (defence-in-depth gap); inconsistent control application
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Affected location: `auth.py:157-189` (`urllib_transport`), used by `build_client_credentials_request` callers at `auth.py:371,405`; compare `graph.py:75-83` (`_NoRedirect`, `_OPENER`)
- Evidence: `graph.py` deliberately installs a `HTTPRedirectHandler` subclass that refuses redirects and builds a dedicated opener, and additionally gates every URL through `is_graph_url()` before attaching a bearer token. `auth.py`'s transport calls bare `urllib.request.urlopen(...)`, which uses the default opener and therefore the default redirect handler, and it applies no check on the responding URL. I inspected `urllib.request.HTTPRedirectHandler.redirect_request` in the running interpreter (CPython 3.14.6): for a `POST`, codes 307/308 raise `HTTPError` (so the body is **not** re-sent to a new host — the client secret is not forwarded), while 301/302/303 are converted to a `GET` with `Content-Type`/`Content-Length` stripped and no `data`. So no secret disclosure exists on this path; what remains is that a 302 from the token endpoint would be followed to an arbitrary host and that host's JSON body parsed at `auth.py:184-189`, and a `200` containing `access_token` would then be installed as the session token by `start_app_only`/`_renew_app_only`.
- Attack preconditions: the attacker must control responses that appear to come from `https://login.microsoftonline.com` — i.e. a TLS-intercepting proxy whose CA the machine trusts, a compromised local trust store or `hosts` entry, or compromise of the Microsoft endpoint itself. TLS certificate verification is on by default in `urlopen`, so a plain network attacker cannot reach this.
- Impact: installation of an attacker-chosen bearer string as the in-memory access token, and one outbound `GET` to an attacker-chosen URL. The injected token is only ever sent to `graph.microsoft.com` (`graph.py` refuses non-Graph hosts), so it does not become a credential-exfiltration channel; the practical effect is failed Graph calls and a misleading "signed in" state.
- Exploitability: low — requires an already-privileged position on the host or in its trust chain.
- Recommended remediation: reuse the `graph.py` pattern for the identity transport: build a dedicated opener with a no-redirect handler, and/or assert the final response URL's host is exactly `login.microsoftonline.com` before parsing. This makes the two egress paths consistent and removes the asymmetry a future reader could mistake for a deliberate difference.
- Verification method: unit test that a mock/stub transport chain returning a 302 to another host yields a failure label rather than an installed token; plus a static assertion that `auth.py` uses a no-redirect opener, mirroring the existing `graph.py` tests.
- Disposition: `open`

### SEC-003: The new `POST /api/auth/app` endpoint gives any local process an unauthenticated credential-validation and outbound-request primitive

- Fingerprint: `careview/m2/server/app-only-endpoint-local-credential-oracle`
- Category/reference: CWE-306 (missing authentication for critical function) within an explicitly accepted boundary; abuse-case enumeration gap
- Severity: `low`
- Confidence: `high`
- Blocking: `no`
- Affected location: `server.py:289-297,310-311,347-372`
- Evidence: `do_POST` gates on the `Host` allowlist (`server.py:290`) and `origin_allowed` (`server.py:295`). Both are headers, so they stop a browser page on another origin but not a non-browser local process, which sets them freely — this is the accepted `RISK-002` position (`ROADMAP.md` v4 line 291, `DECISION-014` scope item 2). What is new in M2 is *what* an unauthenticated local caller can now make the server do: submit arbitrary tenant/client-ID/secret triples and read a success/failure verdict (`200 {"state":"success"}` vs `502 {"error":"provider_error"}`), i.e. use CAreview as a credential-validation oracle and as a trigger for arbitrary outbound client-credentials requests to any tenant; and supersede the owner's live session at will (`start_app_only` clears prior state at `auth.py:360-370`), a silent denial of service. Neither the credential-oracle nor the session-supersession abuse case is named in `RISK-002`, `RISK-005`, `DECISION-014`, or `docs/security-boundaries.md`, which frame the widened risk as exposure *of* the retained secret. I confirmed the secret itself cannot be read back out: no endpoint returns or reflects it, and there is no auth-status GET.
- Attack preconditions: code execution as the same OS user (or another local user able to reach `127.0.0.1:8765`) while the server is running. No CAreview credential is needed.
- Impact: local credential-testing without the attacker's own process appearing in the tenant's telemetry under its own identity; unbounded attacker-triggered egress to `login.microsoftonline.com`; silent takeover/denial of the owner's session. All are strictly weaker than what local code execution already grants (direct process-memory access to the same secret), which is why this is rated low.
- Exploitability: trivial once local execution exists; not reachable from a remote origin, thanks to the Host/Origin gates and CSP.
- Recommended remediation: no code change is required to keep the accepted posture. Recommend (a) adding these two abuse cases explicitly to `RISK-002`'s text so the human's acceptance covers what the endpoint actually enables, and (b) if the human later wants to narrow it, the previously-declined loopback PIN/token gate (`DECISION-014` item 2) or a per-process token echoed in the served page would close it. As reviewer I neither accept nor broaden this risk.
- Verification method: documentation diff review at acceptance; if a gate is later added, a test that an unauthenticated `POST /api/auth/app` with valid Host/Origin is rejected.
- Disposition: `risk-candidate` (human decision at M2 acceptance)

### SEC-004: `_reject()` responses on the auth endpoints omit `Cache-Control: no-store`

- Fingerprint: `careview/m2/server/reject-path-missing-no-store`
- Category/reference: CWE-525 (information exposure through caching) — defence in depth
- Severity: `info`
- Confidence: `high`
- Blocking: `no`
- Affected location: `server.py:175-182` (`_reject`), reached for `/api/auth/app` at `server.py:354,357,360` and for the invalid-body path at `server.py:301`
- Evidence: `_send_json` supports `no_store=True` and the app-only success and `AuthError` paths use it (`server.py:370,372`), but `_reject` never sets the header. `ROADMAP.md` v4 `ISSUE-0009` requires "`no-store` on any response reflecting auth state". The reject bodies contain only fixed labels (`{"error": "invalid tenant"}` etc.) and no secret — `tests/test_server.py::test_secret_absent_from_every_response_body` scans all eleven validation-rejection bodies in three encodings and they are clean — and browsers do not cache `POST` responses by default, so the practical exposure is nil.
- Attack preconditions: an intermediary or browser cache that stores POST responses; none exists on the loopback path.
- Impact: none identified beyond inconsistency with the endpoint's own stated header policy.
- Exploitability: none identified.
- Recommended remediation: set `Cache-Control: no-store` in `_reject` unconditionally, or at least for `/api/auth/*` paths.
- Verification method: extend the existing `no-store` assertions in `tests/test_server.py` to the 400 paths.
- Disposition: `open` (cosmetic/consistency)

### SEC-005: In-process secret exposure is irreducible in stdlib Python and is stated more absolutely in the docs than the implementation can guarantee

- Fingerprint: `careview/m2/auth/secret-inmemory-not-zeroizable`
- Category/reference: CWE-316 (cleartext storage in memory); documentation-accuracy note
- Severity: `info`
- Confidence: `high`
- Blocking: `no`
- Affected location: `auth.py:236,382-386,405`; `server.py:282-287,350`; `docs/security-boundaries.md:97-118`
- Evidence: the secret exists as an immutable `str` in `AuthManager._app_only_secret` and, transiently, as the raw request bytes (`server.py:282`), the decoded JSON object, the `urlencode`d form string and its UTF-8 encoding (`auth.py:134-141`), and JS strings in the browser tab. `logout()` rebinds the attribute to `None` but cannot zeroise the underlying buffer; copies persist until garbage collection and remain recoverable from a core dump, a swapped page, a debugger attached as the same user, or a hibernation image. This is inherent to the stdlib-only constraint, not a defect in the change. The mitigation list in `docs/security-boundaries.md` reads as a closed set ("cleared immediately on logout") without noting that clearing is a rebinding, not an erasure.
- Attack preconditions: same-user code execution, debugger attach, or access to a memory image/swap of the host.
- Impact: recovery of a live client secret with whatever application permissions the app registration holds (`RISK-006`).
- Exploitability: low — strictly requires a position that already compromises the host.
- Recommended remediation: no code change available within the stdlib constraint. Add one sentence to `docs/security-boundaries.md`'s M2 bullet stating that in-memory clearing is a rebinding and that process memory, core dumps, and swap remain out of scope, so the mitigation list is not read as an erasure guarantee.
- Verification method: documentation review at acceptance.
- Disposition: `open` (documentation)

### SEC-006: Candidate-SHA binding in the status record is stale relative to the SHA under review, and the milestone record's "working tree clean" claim is not currently true

- Fingerprint: `careview/m2/governance/candidate-sha-binding-drift`
- Category/reference: review-integrity / evidence-binding hygiene
- Severity: `info`
- Confidence: `high`
- Blocking: `no`
- Affected location: `project/status/CURRENT.md` (Summary, "Reviewed product commit" row); `project/milestones/M2.md:5-6,42-53`
- Evidence: `project/status/CURRENT.md` names the frozen candidate as `98be0bc562de8f7cf52e3019715bc4cff571ad91`, and `project/milestones/M2.md:5` repeats it while stating that each review targets the literal current `main` HEAD. The SHA I was assigned and that `git rev-parse HEAD` returns is `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`, two commits later. I verified independently that `git diff --stat 98be0bc..9c01749` touches only `project/milestones/M2.md`, `project/status/CURRENT.md`, and one report file under `project/reviews/milestones/` — no product file, and `git diff 9d346f6..HEAD -- '*.py' web/` is empty, so all M2 product code has been unchanged since `ISSUE-0010` merged. The review target is therefore correct and this is **not** a wrong-target review. Separately, `project/milestones/M2.md:6` asserts "working tree clean" while the tree currently holds an untracked in-flight peer report and `main` is 2 commits ahead of `origin/main`; the "Four mandatory reviews" table still carries `<pending>` in all four Reviewed-SHA cells.
- Attack preconditions: N/A.
- Impact: a later reader could bind M2's evidence to the wrong SHA, or treat a superseded record as current. Given the reruns already performed, the risk is confusion rather than unreviewed code.
- Exploitability: N/A.
- Recommended remediation: when the four round-1 reports are recorded, update `project/status/CURRENT.md` and `project/milestones/M2.md:5` to name `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d` as the reviewed candidate, fill the four Reviewed-SHA cells, and restate the tree-identity claim as of the commit rather than the live working tree.
- Verification method: `git rev-parse HEAD`, `git diff --stat 98be0bc..HEAD`, and `git status` against the recorded values.
- Disposition: `open` (record hygiene; for the author/human, not a source change)

### SEC-007: Declared evidence gaps — no live tenant and no browser automation

- Fingerprint: `careview/m2/evidence/no-live-tenant-no-browser-automation`
- Category/reference: evidence gap / unverifiable claim
- Severity: `info`
- Confidence: `high`
- Blocking: `no`
- Affected location: `project/milestones/M2.md:37-38`; `tests/test_ui_safety.py`; `project/handoffs/ISSUE-0010-handoff.md`
- Evidence: I could not exercise a real client-credentials sign-in (a protected action requiring named-tenant human approval, correctly not performed), so the end-to-end secret lifecycle was verified only against mock transports. Browser-side behaviour — that `type="password"` masks the field, that `clearAppOnlySecretField()` actually empties the DOM node at runtime, that no extension or password manager captures the value, that no browser form-history entry is created — is asserted only statically over the text of `web/app.js` and `web/index.html` (`tests/test_ui_safety.py::AppOnlyModeToggleTests`, which are substring assertions, not executions) plus a human-performed manual walkthrough recorded in a handoff that I can read but cannot independently reproduce. `RISK-005` correctly describes browser-side exposure as mitigated, not eliminated. Both gaps are declared in the milestone record rather than hidden, which is why this does not make the review inconclusive.
- Attack preconditions: N/A.
- Impact: residual uncertainty that a runtime-only defect in secret clearing or a live-flow failure would not have been caught by this review.
- Exploitability: N/A.
- Recommended remediation: none required for M2 as scoped. If the human later approves a live-tenant run, treat the app-only lifecycle (entry → sign-in → expiry/renewal → logout) as the named check to repeat with a throwaway secret that is rotated immediately afterwards.
- Verification method: future live-tenant verification under separate human approval; optional headless-browser assertion of field clearing if a browser toolchain is ever approved.
- Disposition: `open` (accepted gap, declared)

## Conclusion and limitations

**Outcome: `PASS_WITH_NOTES`** for candidate `9c01749b221d6f7f2d8ff9ca6282cf9172477a3d`, under the scope and evidence above.

I found no critical or high finding. The named M2 security check — the end-to-end client-secret lifecycle from form field, through the loopback `POST /api/auth/app` body, into server-process memory, retained for the session with silent renewal, then cleared — is implemented as `DECISION-014` and `ROADMAP.md` v4 describe it, and the anti-leak controls are stronger than the minimum: the fixed local error-label mapping in `_classify_app_only_error` prevents even a hostile provider response from echoing the secret back into an exception or a response body, and the tests exercise the literal, URL-encoded, and JSON-escaped forms across every failure path. Server-side validation runs before any value is retained or transmitted, the tenant value cannot redirect the request to another host, egress is confined to Microsoft's token and Graph endpoints, no dependency was added, and all three required checks re-ran clean at this exact SHA under my own execution.

The two notes that most warrant the human's attention at acceptance are **SEC-001** (a rotated or revoked secret is replayed to Microsoft on every subsequent request, and stays in memory while the UI reports signed-out — an operational case, not an attack) and **SEC-003** (the new endpoint gives any local process a credential-validation oracle and a session-supersession primitive; this sits inside the already-accepted `RISK-002` boundary, but those two specific abuse cases are not named in the risk text the human accepted). Neither blocks. SEC-002, SEC-004, and SEC-005 are defence-in-depth and documentation-accuracy items; SEC-006 and SEC-007 record binding hygiene and declared evidence gaps.

Limitations: this review is static analysis, targeted dynamic probing with mock transports, and record inspection by one model against one commit. No live tenant, no real secret, no browser execution, no memory forensics, and no third-party scanner were involved. `PASS_WITH_NOTES` means only that these checks passed for this SHA under the documented scope and available evidence; it is not a statement that CAreview is secure, certified, or free of vulnerabilities, and it does not accept any risk — risk acceptance and the milestone decision remain the human's alone. Per `AGENTS.md`, `PASS_WITH_NOTES` requires an explicit human decision and does not advance the gate automatically.

Any repair that creates a new milestone candidate invalidates both general and
both security reports; rerun all four against the one new SHA.
The milestone workflow permits at most two security-remediation cycles and an
absolute maximum of five iterations for any loop. Exhaustion blocks for the
human.
