# Claude response to Codex plan review (round 2)

**Reviewed roadmap:** `ROADMAP.md` v2 at `4daf03ca5be5ee07f713f77cb12f3deda54e72b3`
**Codex report:** `project/reviews/plans/ROADMAP-4daf03ca5be5-codex.json` (outcome `BLOCKED`)
**Responder:** Claude planning task, 2026-07-24
**Result of this round:** roadmap revised to v3. This is the **second** revision
round; per `docs/workflow.md`, remaining unresolved items are presented to the
human rather than looping further.

Round-1 findings (F-001..F-005) were confirmed resolved by Codex round 2 (it
states target identity is correct and the roadmap is well structured and
dependency-ordered). Round-2 findings:

| Finding | Disposition | Action |
|---|---|---|
| F-001 No DNS-rebinding mitigation for the loopback API | Accepted | ISSUE-0001: add a `Host`-header loopback allowlist (reject non-loopback Hosts) + an Origin helper for `/api/auth/*`, with tests for accepted/rejected Hosts. Recorded as a roadmap security assumption. |
| F-002 Break-glass rule has no evidence source | Accepted | ISSUE-0003 data contract gains an optional local, user-supplied sanitized break-glass ID input; ISSUE-0004's break-glass rule is *not evaluable* without it. No IDs committed. |
| F-003 M1 completion contradicts live-verification policy | Accepted | ROADMAP M1 exit criteria + success measure + M1.md: M1 completes on mocked/fixture evidence; live sign-in/fetch is a separately approved protected step recorded as a residual evidence gap the human may accept — never an M1 gate. |
| F-004 (BLOCKER) Governance validator could not run in the review sandbox | Evidence provided out-of-band; **structural limitation presented to the human** | Per the finding's own remediation ("do not change the candidate; rerun the validator in an environment with a writable temp dir and record the result"), the validator was run against the candidate. See evidence below. |

## F-004 governance-validation evidence (run out-of-band)

`python3 scripts/validate_repo.py` was run against the candidate tree in a normal
environment (writable temp dir). It completes and reports exactly one error:

```
Repository validation failed with 1 error(s):
- wrong stage did not fail before provider execution/report staging: exit 78, marker=True, reports=1,
```

That single error is a **latent bug in the validator's own wrong-stage smoke
test**, not a defect in this roadmap: the test copies the repository's committed
`CURRENT.md` and assumes the repo is never legitimately at `stage:
ROADMAP_REVIEW`. Because we are correctly at `ROADMAP_REVIEW` to run the plan
gate, a plan review is (correctly) accepted, so the negative smoke test no longer
sees a rejection. Every other check — required files, JSON/TOML syntax, Markdown
links, and required workflow language — passes. This validator bug is recorded in
`DECISION-002` notes as a separate follow-up.

Codex cannot reproduce this evidence because its read-only review sandbox provides
no writable temporary directory, so it fails closed to `BLOCKED`. This is a
structural property of the review environment, not a roadmap defect, and it will
recur on every plan review. It is therefore presented to the human for the
roadmap-approval decision.

## Position for the human

Roadmap v3 addresses every actionable Codex finding across both rounds. The only
remaining Codex blocker (F-004) is the review-sandbox's inability to run the
validator; out-of-band validator evidence is recorded above. The two permitted
planning revision rounds are used. The human decides whether to approve roadmap
v3 as-is, or to request a third (confirmatory) Codex review knowing F-004 will
recur.
