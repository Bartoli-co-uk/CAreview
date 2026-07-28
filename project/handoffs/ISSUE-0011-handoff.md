# Claude handoff: ISSUE-0011, round 0

**Claude issue task:** `ISSUE-0011 m2-docs implementation`
**Approved issue:** `project/issues/ISSUE-0011.md` at this commit
**Starting SHA:** `4f35275d004265ee152348e7e3d1f7b9f6a62cc6`
**Candidate SHA:** this commit (branch HEAD); the launcher records the full SHA
**Created at:** `2026-07-28`

## Outcome

Implemented in full. `README.md` and `docs/security-boundaries.md` now
document the complete M2 dual-mode implementation. No product source was
touched.

### `README.md`

- Status banner updated: "MVP complete, dual-mode auth complete"; the
  tracked live-sign-in gap now covers both modes.
- "What it does" step 1 notes the optional app-only mode and links to its
  section.
- New **"App-only mode (advanced)"** section: the exact prerequisite (a
  user-owned app registration with *application* `Policy.Read.All`
  already consented, its client ID, and a generated client secret);
  explicit statement that CAreview never creates/modifies the app
  registration; recommendation to use a dedicated app registration scoped
  to only `Policy.Read.All` (`RISK-006`); the full secret lifecycle
  (sent once over the loopback POST body, retained in server memory for
  the session for silent renewal, never persisted, cleared on sign-out);
  how to rotate/revoke access (via the Entra portal, then sign out/back in
  in CAreview); and an explicit statement that certificate-based auth is
  unsupported this release and is a deferred future enhancement needing
  its own dependency-approval decision.
- New **"End-to-end walkthrough"** section: numbered steps for each mode,
  with the one live step in each (approving the device code / submitting
  real app-only credentials) explicitly labeled as a protected action the
  reader performs themselves, plus a reminder that the sample-analysis
  path exercises the identical rendering code without any live step.
- Corrected two stale test-count references (`85` → `173`).
- "Zero registration, zero build" design-goal bullet qualified as
  "by default" with a pointer to the opt-in app-only section.
- "How the code fits together" table's `auth.py` row updated to describe
  both auth modes.
- "Security model" section: added a bullet on the app-only secret's
  session-memory retention and the widened trust boundary, with pointers
  to the app-only section and `docs/security-boundaries.md`; corrected the
  "no secrets" bullet, which previously claimed absolutely "there is no
  client secret" (true only for device-code mode).
- "Known limitations" table: added `RISK-005` and `RISK-006` rows;
  broadened the "Live sign-in unverified" and `RISK-001`/`RISK-002` rows
  to cover both modes.
- Added Contents entries for the two new sections.

### `docs/security-boundaries.md`

Extended "CAreview application boundaries":

- The "tokens are ephemeral" bullet now covers both auth modes.
- The "no secrets" bullet corrected to not claim there is categorically no
  client secret.
- New bullet: the app-only trust-boundary delta — session-retained client
  secret, why (`get_token()` silent renewal), the widened `RISK-002`, and
  every mitigation already implemented in `ISSUE-0008`/`ISSUE-0009`/
  `ISSUE-0010` (no persistence, never in a returned value/exception/
  `repr()`, stable local error labels only, cleared on logout/
  supersession, and the browser-side `RISK-005` mitigations).
- New bullet: `RISK-006` (the `.default` scope can't be narrowed) as an
  accepted, not mitigated, residual.
- New bullet: certificate-based app-only auth is out of scope this
  release, recorded as a deferred future enhancement.
- "Least privilege" bullet extended to describe both modes' scope
  behavior.

## Changed files

| Path | Change and reason |
|---|---|
| `README.md` | Dual-mode documentation, new App-only mode and End-to-end walkthrough sections, stale test-count fixes, Security model / Known limitations updates. |
| `docs/security-boundaries.md` | App-only trust-boundary delta, widened `RISK-002`, `RISK-006` residual, certificate deferral note. |
| `project/issues/ISSUE-0011.md` | New issue record. |

## Decisions and assumptions

- Added the "End-to-end walkthrough" section as new top-level content
  rather than folding it into "Quick start", since the roadmap's
  acceptance criteria specifically calls for "a documented end-to-end
  walkthrough ... for each mode" with live steps explicitly marked — this
  reads as a distinct, complete reference a reader can follow start-to-
  finish, separate from "Quick start"'s narrower first-run guidance.
- Fixed the two stale "85 tests" references to the real current count
  (173, confirmed by running the suite) as part of this documentation
  pass, even though `ISSUE-0011`'s acceptance criteria don't name this
  specifically — README accuracy about the test suite is squarely within
  this issue's allowed paths and objective, and leaving a known-wrong
  number uncorrected while doing a full documentation pass would be
  worse, not smaller-scoped.
- Did not add a dedicated `RISK-003`/`RISK-007`/`RISK-008` row to the
  README's "Known limitations" table — those are process/implementation
  risks (accidental logging, hourly re-auth now resolved, a real secret
  landing in a tracked file) rather than something an end user reading
  the README needs to plan around; they remain fully documented in
  `ROADMAP.md`'s risk table, which the README already links to via
  "tracked in `ROADMAP.md`".
- Did not touch `SECURITY.md` — it already points to
  `docs/security-boundaries.md` for "wider operating boundaries" and
  needs no mode-specific content of its own.

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| README documents both auth modes | "What it does" step 1; "App-only mode (advanced)"; "How the code fits together" `auth.py` row; "Security model" | Met |
| Exact app-only prerequisite stated | "App-only mode (advanced)" — Prerequisite bullet list | Met |
| CAreview never creates the app registration | "App-only mode (advanced)" — explicit sentence | Met |
| Certificates unsupported, deferred enhancement | "App-only mode (advanced)" — closing paragraph | Met |
| Secret is session-only with silent renewal | "App-only mode (advanced)" — "What happens to the secret" | Met |
| Rotation/revocation documented | "App-only mode (advanced)" — "To rotate or revoke access" | Met |
| `docs/security-boundaries.md` records trust-boundary delta and widened `RISK-002` | New bullet in "CAreview application boundaries" | Met |
| End-to-end walkthrough per mode, live steps marked as reader's protected action | "End-to-end walkthrough" section | Met |
| No live run required to complete | No live sign-in performed; see Verification below | Met |
| `unittest`, `py_compile`, `validate_repo.py` pass | See Verification below | Met |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | `Ran 173 tests ... OK`, exit 0 | None — no source changed, count unaffected |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0, no output | None |
| Governance | `python3 scripts/validate_repo.py` | "Repository validation passed (67 required files checked)." — includes Markdown link/anchor validation, which checks the new "App-only mode (advanced)" and "End-to-end walkthrough" Contents links resolve | None |
| Documentation walkthrough (non-live steps only) | Started `python3 server.py` from the working tree; `curl /api/health` → `{"status": "ok"}`; `curl /` confirmed both `id="app-only-toggle-btn"` and `id="tenant"` are present (both modes' entry points exist as documented); `curl /sample-data.json` confirmed the non-live walkthrough alternative renders (5 policies, score 88) | Matches the documented steps | The one live step per walkthrough (approving a device code / submitting a real app-only secret) was intentionally not performed — protected action, explicitly the reader's own step per the walkthrough text |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

This issue *is* the documentation change — see Outcome above.

## Security and privacy

- Threat-model change: none. This issue documents residuals
  (`RISK-002` widened, `RISK-005`, `RISK-006`) already introduced and
  accepted by prior M2 issues and `DECISION-014`; it introduces nothing
  new.
- Residual risk/uncertainty: none identified beyond what is already
  accepted and now documented.
- Protected action attempted: No. No live tenant sign-in; the server was
  run locally against its own static assets and sample data only, then
  stopped.

## Review request

- Base SHA: `4f35275d004265ee152348e7e3d1f7b9f6a62cc6`
- Head SHA: (this commit; recorded by the launcher)

## Repair round 1

Round-0 Codex review
(`project/reviews/issues/ISSUE-0011-b0b91742ec6c-codex.json`, candidate
`b0b91742ec6cdd8925b69fcdc45ae533a5d3b9f2`) returned `BLOCKED` with two
findings:

- **F-001 fix (medium):** the "App-only mode (advanced)" section said the
  secret is sent to CAreview's local server "never anywhere else," which
  is materially inaccurate — the local server necessarily forwards it to
  Microsoft's tenant token endpoint (`login.microsoftonline.com`) for the
  initial client-credentials request and again on every silent renewal;
  that *is* the mechanism, not an extra leak, but the original wording
  read as claiming no second hop existed at all. Rewrote the "What happens
  to the secret" list to describe both hops precisely: browser → local
  server (once, never to any other page/host/process), then local server →
  Microsoft's token endpoint only (on acquisition and every renewal),
  never returned to the browser and never sent to any other host.
- **F-002 fix (high):** no durable repository record authorized starting
  `ISSUE-0011` — `DECISION-020` explicitly scopes itself to `ISSUE-0010`
  only, and the human's actual "begin ISSUE-0011" instruction existed only
  in chat at the time of the round-0 candidate. Fixed by recording
  `project/decisions/DECISION-021-issue-0011-start-authorization.md`,
  which quotes the exact instruction, mirroring the
  `DECISION-018`/`ISSUE-0009` precedent for the same gap.
- Rechecked after both fixes: `python3 -m unittest discover -s tests` →
  173 passed, exit 0 (no product/test source changed, so the count is
  unchanged); `python3 -m py_compile $(git ls-files '*.py')` → exit 0;
  `python3 scripts/validate_repo.py` → "Repository validation passed (67
  required files checked)."
- This is round 1 of at most two permitted issue repair rounds.

## Round-1 review result and stop point

The round-1 Codex re-review
(`project/reviews/issues/ISSUE-0011-e878cdcd979b-codex.json`, candidate
`e878cdcd979b7be87ff20cc986cb16d0d457dfe0`) returned `BLOCKED` with
`findings: []` — zero actionable defects. Its evidence explicitly confirms
both round-0 findings were addressed: the README now accurately describes
both secret-transmission hops, and `DECISION-021` durably records the
start authorization. The sole blocker is the same sandbox
execution-evidence limitation present in round 0: the read-only checkout
cannot bind loopback sockets, write `__pycache__`, or create a writable
temp directory, so the three required repository-wide checks — and the
non-live server walkthrough — cannot complete independently inside the
review process itself, even though they pass locally and their real
output is recorded above. Only 1 of 2 permitted repair rounds was needed.

Per `AGENTS.md`'s completion standard ("the human has made any required
advance or merge decision") and the `DECISION-010`/`DECISION-016`/
`DECISION-017`/`DECISION-019`/`DECISION-020` precedent — the same
sandbox-only-blocker pattern on every prior M2 issue, all of which
required an explicit human closeout decision despite zero product
findings — this Claude task stops here and presents the clean round-1
result to the human rather than unilaterally marking `ISSUE-0011`
complete or merging it. `ISSUE-0011` is the final planned M2 issue;
merging it completes M2's issue set, though M2 acceptance itself is a
separate milestone gate (four fresh reviews against one frozen candidate)
that this task does not initiate.
