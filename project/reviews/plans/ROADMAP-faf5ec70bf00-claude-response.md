# Claude response to Codex plan review (round 6 overall; confirmatory round 4 for v4) — FINAL for v4

**Reviewed roadmap:** `ROADMAP.md` v4 candidate at `faf5ec70bf00d364c848be057e6422905e337619`
**Codex report:** `project/reviews/plans/ROADMAP-faf5ec70bf00-codex.json` (outcome `BLOCKED`)
**Responder:** Claude planning task, 2026-07-27
**Result of this round:** three corrections applied at a new commit. This is
the repository's **absolute five-iteration cap** (`AGENTS.md`: "No review,
repair, or reconciliation loop may exceed five total iterations") for the v4
planning loop, counting the initial review plus the two permitted revisions
plus the two confirmatory rounds already run at the human's direction. Per the
human's explicit decision, these findings are corrected here and then
presented directly for the human's exact roadmap approval — **no further
automated Codex plan review will be launched for v4.**

| Finding | Disposition | Action |
|---|---|---|
| F-001 (BLOCKER) Governance validator could not execute in the review sandbox (no writable temp dir) | Evidence provided out-of-band; **structural review-sandbox limitation, not a roadmap defect** — the same class of finding at every prior round | `python3 scripts/validate_repo.py` run against this exact candidate outside the sandbox: "Repository validation passed (67 required files checked)." `python3 -m unittest discover -s tests`: 83 passed. `python3 -m py_compile $(git ls-files '*.py')`: exit 0. |
| F-002 `ISSUE-0009` validated `tenant`/`client_id`/`client_secret` only for presence and type, with no length/format bound, allowing an oversized value (up to the existing 64 KiB body limit) to reach retention and outbound transport before any rejection | Accepted | Added explicit bounded-format criteria to `ISSUE-0009`: `tenant` must be a GUID or DNS-style domain under a documented max length (and still rejects `organizations`/`common`/`consumers`); `client_id` must match the Entra app-ID GUID shape; `client_secret` must be non-empty under a documented generous max length (e.g. 512 chars). All three reject with 400 before any outbound identity request or retained state, with boundary tests for minimum/maximum/one-over-maximum/malformed values. |
| F-003 Literal-only scrubbing of the submitted secret from provider error text cannot catch transformed representations (URL-encoded, JSON-escaped, split) of an untrusted provider response | Accepted, and adopted the stronger remediation Codex proposed | Replaced "truncate and scrub provider error text" with **never returning or logging raw provider error text at all** — every provider/network failure maps to one of a small, fixed set of stable local labels (e.g. `invalid_tenant`, `provider_error`, `network_error`). Updated the `ISSUE-0008` and `ISSUE-0009` acceptance criteria accordingly, including a test that a mock provider error containing the secret literally, URL-encoded, JSON-escaped, or split across surrounding text never reaches any response, exception, log, or `repr()`. |
| F-004 (advisory, low) Top-level project outcome, stakeholder table, and project definition-of-done still read as device-code-only and left M2's relationship to "M1 = the whole MVP" ambiguous | Accepted | Updated the Project outcome and stakeholder/consent rows to describe the opt-in app-only mode (and that certificate auth is deferred), and clarified in the project definition of done that M2, once approved, is an extension of the completed M1 MVP rather than a redefinition of it. |

## F-001 evidence (run out-of-band, this exact candidate before the final three fixes; re-confirmed after)

```
$ python3 scripts/validate_repo.py
Repository validation passed (67 required files checked).

$ python3 -m unittest discover -s tests
Ran 83 tests in 11.122s
OK

$ python3 -m py_compile $(git ls-files '*.py')
(exit 0)
```

## Position for the human

This is the final planning round for v4 under the repository's own iteration
cap. Every actionable Codex finding across all four review rounds (initial,
two permitted revisions, and two confirmatory rounds) has been addressed; the
only recurring blocker (the review sandbox's inability to run real checks) is
a documented environmental limitation with out-of-band evidence at every
round, consistent with the precedent set for the v3 roadmap. No further
automated Codex plan review will be launched for this candidate. The human
now decides whether to approve this exact v4 commit.
