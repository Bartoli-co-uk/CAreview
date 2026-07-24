# Claude response to Codex plan review (round 1)

**Reviewed roadmap:** `ROADMAP.md` v1 at `691b1427de57549baa8fb6ff2395b0d1399587a5`
**Codex report:** `project/reviews/plans/ROADMAP-691b1427de57-codex.json` (outcome `BLOCKED`)
**Responder:** Claude planning task, 2026-07-24
**Result of this round:** roadmap revised to v2; a fresh Codex re-review follows.

| Finding | Disposition | Action |
|---|---|---|
| F-001 Launcher omitted required target identity | Partially accepted (tooling, not roadmap content) | Clarify plan-mode binding convention in `prompts/03-codex-plan-review.md` so the empty Target ID / base is understood as intentional (plan reviews bind by Target record + Target commit), and `target_id` is emitted as `""`. Does not change roadmap content. |
| F-002 Live auth bypasses protected-action gate | Accepted | ROADMAP + ISSUE-0002/0003: mark real device-code sign-in and live Graph fetch as protected actions needing separate human approval naming the tenant; make mocked checks the default completion gate; record live evidence only after approval. |
| F-003 Analyzer sequenced before data contract | Accepted | ROADMAP: resolve A3 before ISSUE-0003; add a normalized data-contract requirement. ISSUE-0003 defines the contract; ISSUE-0004 defines required source fields and unknown/not-applicable behaviour per rule (never score missing evidence as pass/fail). |
| F-004 Token lifecycle incomplete | Accepted | ISSUE-0002: add acceptance criteria for device-code expiry, server-controlled polling cadence, opaque bounded handle, logout/cancellation + memory clear, access-token-expiry behaviour, explicit refresh-token decision, and a single-concurrency policy. |
| F-005 UI untrusted-content protection | Accepted | ISSUE-0005: add acceptance/security criteria requiring text-not-HTML insertion of tenant/finding strings, no dynamic code, no external assets, a restrictive CSP, and `no-store` on sensitive API responses. |

## Notes on F-001 and evidence limitations

- The launcher intentionally passes no base commit and an empty Target ID for
  `plan` mode; its own `validate_semantics` requires `target_id == ""` for plan.
  The target is bound by `Target record: ROADMAP.md` and the `Target commit` SHA,
  which matched HEAD. The prompt clarification records this convention so the
  reviewer treats it as intended rather than missing evidence. This is a
  workflow-prompt clarification, not a weakening of any gate, and is noted for the
  human at the roadmap-approval gate.
- Codex's other limitations (no writable temp dir to run `validate_repo.py`; no
  live-tenant network verification) are inherent to a read-only, no-network plan
  review and are acknowledged evidence gaps, not roadmap defects.
