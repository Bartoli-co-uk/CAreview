<!-- claudex-state
stage: ROADMAP_REVIEW
active_issue: none
active_milestone: none
-->

# Current workflow status

Update this file whenever a human approval, issue completion, milestone gate, or
material blocker changes what may happen next. Commit the update with its
supporting artifact; do not use chat as the only status record.

Keep the `claudex-state` block above synchronized with the table. The review
launcher reads that small committed block to reject a review for the wrong
workflow stage, issue, or milestone; it does not replace the human approval
records described below. `ROADMAP_REVIEW` means a roadmap candidate is
committed and awaiting its mandatory fresh Codex plan review before the human
can approve it; no issue may start while this stage is set.

## Summary

M1 (the original approved MVP) remains complete and accepted (`DECISION-012`);
nothing about it has changed. The human has approved a brief v2 amendment
(`DECISION-013`) adding an opt-in app-only (client-credentials) sign-in mode
beside the unchanged default device-code flow, and a `ROADMAP.md` v4 candidate
implementing it has been drafted and committed as `M2` (five issues,
`ISSUE-0007`..`ISSUE-0011`). Per `AGENTS.md`, implementation cannot begin until
that exact roadmap version is both reviewed by a fresh Codex plan review and
approved by the human — neither has happened yet. The mandatory Codex CLI is
not available in this session's environment (`codex: command not found`),
which is an active blocker on the review step, not something an agent may
skip or substitute.

| Field | Current value |
|---|---|
| Stage | `ROADMAP_REVIEW` — v4 roadmap candidate committed, awaiting Codex plan review and human approval; no active issue |
| Project description | `project/intake/PROJECT_DESCRIPTION.md`; supplied |
| Project brief | `project/brief/PROJECT_BRIEF.md` v2; APPROVED (DECISION-013, binds `98feea6`); v1 remains APPROVED (DECISION-001) for the M1 scope it covers |
| Brief approval | `project/decisions/DECISION-001-brief-approval.md` (v1, binds `179a023`); `project/decisions/DECISION-013-brief-v2-approval.md` (v2, binds `98feea6`) |
| Roadmap | `ROADMAP.md` v3 remains the only **approved** roadmap (DECISION-003, binds `125d74f`) — governs the complete M1 scope. **v4 is a committed, unapproved draft** adding `M2`; no Codex plan review has run against it |
| Roadmap approval | `project/decisions/DECISION-003-roadmap-approval.md` (v3 only). v4: not yet recorded |
| Active milestone | None. `M1` — `COMPLETE`, accepted (`DECISION-012`). `M2` — `PLANNED`, unapproved, blocked on roadmap v4 review/approval |
| Active issue | None. `ISSUE-0007`..`ISSUE-0011` are `PENDING` in the unapproved v4 draft; none may start |
| Issue repair round | None open |
| Reviewed product commit | `6311a11a48a0a7e51e83a14ca4081d431cb46698` — the frozen M1 round-2 candidate. No product file has changed since; all commits since are documentation/planning only |
| Latest implementation handoff | `project/handoffs/ISSUE-0006-handoff.md` (M1; no M2 handoff exists yet) |
| Latest milestone reviews | Round 2 M1 reviews only, bound to `6311a11a`: `M1-r2-claude-general.md` (PASS_WITH_NOTES), `M1-af6d10b22e3f-codex-general.json` (BLOCKED — execution-evidence limitation only), `M1-r2-claude-security.md` (PASS_WITH_NOTES), `M1-059b0ae82122-codex-security.json` (BLOCKED — execution-evidence limitation only). No M2 milestone reviews exist |
| Latest Codex issue review | ISSUE-0006 final `ISSUE-0006-d15f47c5fb15-codex.json` — no product finding; closed per DECISION-010. No Codex review of any kind exists for the v4 roadmap or any M2 issue |
| Completed issues | `ISSUE-0001` `23e6633`; `ISSUE-0002` `3c8fb869`; `ISSUE-0003` `065675e`; `ISSUE-0004` `9f3885b`; `ISSUE-0005` `3dc059f`; `ISSUE-0006` `d15f47c` |
| Last human decision | `DECISION-014` (app-only secret retention model + RISK-002 re-acceptance); also `DECISION-013` (brief v2 approval), `DECISION-012` (M1 acceptance), `DECISION-011`..`001` |
| Open blockers | **Codex CLI unavailable in this environment** (`codex: command not found`, reproduced: `./scripts/run-codex-review.sh plan c8185a0...` → exit 69) — blocks the mandatory review of roadmap v4 per `AGENTS.md` rule 13; this cannot be skipped or substituted. Brief v2 Questions 3 (RISK-002) and 6 (secret retention) are now resolved by `DECISION-014`. **Q5 (tenant-value validation UX) remains open** and gates `ISSUE-0008` specifically, independent of the Codex blocker |
| Tracked follow-up | Live-tenant sign-in verification (M1 scope) — still deferred pending the human's access restrictions (`DECISION-012`); unchanged by this session |
| Next required actor | Human: (1) resolve the Codex-CLI-unavailable blocker (e.g. run the launcher in an environment where Codex is installed and authenticated, and commit the resulting report) so roadmap v4 can be reviewed; and (2) answer brief v2 Questions 3/5/6 before `ISSUE-0008` can start |
| Next permitted action | Once a fresh Codex plan review of the exact v4 commit is obtained and Claude has responded to any findings, the human may approve the exact final v4 roadmap. Only after that may `ISSUE-0007` begin, in a new top-level Claude issue task, on an isolated branch |
| Actions not yet permitted | Any M2 implementation; merge without a clean review; publication; deployment; live tenant auth/fetch in either mode; any other protected action |

## Verification evidence at the reviewed M1 commit

Re-runnable from a clean checkout; see `project/milestones/M1.md` for the
commit-bound record captured at the gate. Unaffected by the v4 roadmap draft
below, since no product file has changed since `6311a11a`.

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 83 passed, exit 0 |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | passed |

## Real checks run against the v4 roadmap candidate (`c8185a0`)

| Check | Command | Result |
|---|---|---|
| Tests | `python3 -m unittest discover -s tests` | 83 passed, exit 0 (unchanged — no product file touched) |
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Governance | `python3 scripts/validate_repo.py` | **exit 1, 1 error**: `wrong stage did not fail before provider execution/report staging: exit 78, marker=True, reports=1`. This is a known, previously documented latent self-test defect (flagged as a non-blocking follow-up in `DECISION-002`'s Notes): `smoke_target_binding_rejections`'s "wrong stage" fixture copies the live working tree and assumes it is never legitimately committed at `stage: ROADMAP_REVIEW`. It now legitimately is, so the fixture's own assumption breaks, not the launcher's real gating behaviour. It is expected to self-resolve once the stage moves off `ROADMAP_REVIEW` (roadmap approval or reversion). Not fixed here: fixing a governance script is itself a protected action needing its own separate human approval, per the same precedent (`DECISION-002`, `DECISION-011`) |
| **Mandatory Codex plan review** | `./scripts/run-codex-review.sh plan c8185a0387d457c48675efeb75484e2a89f9da35` | **exit 69: "Codex CLI is unavailable; no review was recorded."** Real, reproduced command output, not an inference. Per `AGENTS.md` rule 13 this **blocks** roadmap v4 from proceeding to human approval — it is not something an agent may skip, reinterpret, or substitute with a Claude-only review. Resolving this requires running the launcher (or an equivalent fresh, independent, read-only Codex process) somewhere Codex is installed and authenticated, then committing the resulting report under `project/reviews/plans/` |

A fresh task must read `AGENTS.md`, this file, and the artifacts linked here,
then restate the current stage and next permitted action before doing material
work. If a field needed for the next action is missing, contradictory, or stale,
stop and repair the record instead of relying on prior chat.
