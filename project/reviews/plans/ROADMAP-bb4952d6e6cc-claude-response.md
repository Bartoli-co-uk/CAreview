# Claude response: roadmap v6 round-1 Codex plan review

**Reviewed candidate:** `bb4952d6e6cc7a14eda10a30c1dbcb74f09bf8cd`
**Outcome:** `CHANGES_REQUIRED` (5 findings, all `REQUIRED`/blocking)

## F-001 (medium) — Roadmap contradicts itself about the M3 prerequisite

Confirmed and fixed. `ROADMAP.md`'s "Why `M3` is not marked `COMPLETE`" paragraph
was stale leftover text from before M3's milestone gate had run — it predates
`DECISION-032` and was never removed once M3 actually completed. Replaced with
a short historical note pointing at the Milestones table and M3 issue sequence,
which already correctly say `COMPLETE`.

## F-002 (medium) — M4 work-item metadata denies the roadmap association v6 establishes

Confirmed and fixed. All four issue files (`ISSUE-0015`–`ISSUE-0018`) now name
`M4` as their milestone and describe roadmap v6 as the pending, not-yet-approved
governing candidate, while keeping `Status: PLANNED` and both human gates
(roadmap approval, then separate issue-start authorization) explicit.

## F-003 (high) — Terms-of-Use rule can pass when acceptance is optional

Confirmed and fixed. `ISSUE-0016`'s rule spec now requires `grantControls.operator
== "AND"` whenever `builtInControls` is non-empty (an `"OR"`-combined Terms of Use
control is an alternative, not a requirement, and must not pass), and requires
the same "meaningfully scoped" exclusion discipline `mfa-all-users` already uses
(no broad `excludeGroups`/`excludeRoles` on an all-users policy). Added two new
test cases: the OR-operator false-pass and the excluded-scope case.

## F-004 (high) — Admin-rule coverage semantics are ambiguous

Confirmed and fixed for both `ISSUE-0017` and `ISSUE-0018`. Both now specify a
single, explicit effective-coverage algorithm instead of "reuse `mfa-admins`'s
pattern verbatim": qualifying policies are identified first by their specific
control; each qualifying policy's effectively-covered roles account for
`excludeRoles` and for an `includeUsers: ["All"]` policy contributing role
coverage (minus excluded roles); the union of *qualifying* policies' coverage
must equal the full admin-role set, and non-qualifying policies never subtract
from coverage a qualifying policy already established. Three new test cases
were added to each issue (exclusion handling, non-qualifying-overlap
non-interference, and multi-policy union). The existing, already-accepted
`mfa-admins` rule in `rules.py` is explicitly left unchanged — fixing its
same-shaped imprecision is out of scope for this roadmap (would reopen
already-accepted M1/M2 product code, not requested).

## F-005 (medium) — M4 milestone verification omits the frontend integration checks

Confirmed and fixed. `ROADMAP.md`'s M4 milestone-table exit criteria now
additionally require `cd frontend && npm ci && npm run build && npm test`
passing at the same frozen candidate, alongside the Python checks — matching
the rigor M3's own milestone gate already required, since the dashboard
consumes `/api/analysis`'s findings list and none of the four M4 issues touch
`frontend/**` themselves.

## Summary

All five findings are addressed at this commit. Re-running the plan review
against the new candidate next (round 2, within `AGENTS.md`'s two-round
planning-repair budget).
