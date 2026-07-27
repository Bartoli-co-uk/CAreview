# Claude response to Codex plan review (round 3, v4 candidate)

**Reviewed roadmap:** `ROADMAP.md` v4 candidate at `71f7ba60b045abda0f7875e114608b75b076f625`
**Codex report:** `project/reviews/plans/ROADMAP-71f7ba60b045-codex.json` (outcome `BLOCKED`)
**Responder:** Claude planning task, 2026-07-27
**Result of this round:** roadmap v4 revised at a new commit. This is the
**first** revision round for v4 specifically (the v3 rounds recorded above
reviewed a roadmap with no M2 content); per `AGENTS.md`, up to two revision
rounds are permitted before unresolved items are presented to the human.

| Finding | Disposition | Action |
|---|---|---|
| F-001 (BLOCKER) Governance validator could not run in the review sandbox (`FileNotFoundError: No usable temporary directory found`) | Evidence provided out-of-band; **structural review-sandbox limitation, not a roadmap defect** | Same class of limitation recorded for v3 round 2 (`ROADMAP-4daf03ca5be5-claude-response.md`, F-004). `python3 scripts/validate_repo.py` was run against this exact candidate outside the review sandbox: exit 0, "Repository validation passed (67 required files checked)." See evidence below. |
| F-002 M2 exit criteria described the secret lifecycle ending in "discard", contradicting the approved session-retention + silent-renewal model (`DECISION-014`) | Accepted | Rewrote the M2 milestone exit criterion and the Architecture secret-lifecycle bullet to state the actual lifecycle: retained for the session, reused for silent renewal, cleared on logout/supersession/process exit — never a per-request discard. |
| F-003 The "no tracked file" exit criterion was literally impossible given the verification strategy's own committed synthetic test-secret literal | Accepted | Reworded the M2 exit criterion to distinguish the **real** submitted secret (must never appear in any tracked file, response, log, or repr) from the committed **synthetic test sentinel**, which is expected in `tests/` by design and is not itself a violation. |
| F-004 `ISSUE-0009` and `ISSUE-0010`'s required README updates fell outside their own allowed-path boundaries | Accepted | Added `README.md` to both issues' allowed paths in the per-issue boundaries table, so each issue's documentation requirement is satisfiable within its own scope. |
| F-005 `ISSUE-0008` acceptance criteria omitted tests for stale in-flight responses racing a `logout()`/new-start during app-only acquisition or silent renewal | Accepted | Added an explicit acceptance-criteria clause requiring blocking/controllable-mock-transport tests that trigger `logout()` or a new sign-in while an app-only request is outstanding, asserting the stale response cannot install a token or retain/recreate secret state — mirroring the existing device-code `AuthManager`'s generation-counter guard. |

## F-001 governance-validation evidence (run out-of-band)

```
$ python3 scripts/validate_repo.py
NOTICE: PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.
Repository validation passed (67 required files checked).
```

Run locally (writable temp dir available) against the working tree at the time
of the reviewed commit. Codex's read-only review sandbox provides no writable
temporary directory, so the validator cannot run there and the review fails
closed to `BLOCKED` on this point alone, as it did for the analogous v3
round-2 finding. This is a structural property of the review environment, not
a defect in this roadmap, and will recur on every plan review that includes
this check.

## Position for the human

Roadmap v4 (this new commit) addresses every actionable Codex finding (F-002
through F-005). The only remaining Codex blocker (F-001) is the review
sandbox's inability to run the governance validator; out-of-band validator
evidence is recorded above, exit 0. One revision round has been used; up to
one more is permitted before this is presented as an unresolved disagreement.
The human may approve this v4 candidate as-is, or request a confirmatory
re-review knowing F-001 will recur for the same environmental reason.
