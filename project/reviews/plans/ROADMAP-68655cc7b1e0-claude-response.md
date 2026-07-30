# Claude response: roadmap v6 round-2 Codex plan review

**Reviewed candidate:** `68655cc7b1e0a63db3d6b37debf834c126bb60e0`
**Outcome:** `CHANGES_REQUIRED` (3 REQUIRED findings, 1 ADVISORY)

## F-001 (medium) — Admin sign-in-frequency rule can pass without prohibiting persistent browser sessions

Confirmed and fixed. `ISSUE-0017`'s qualifying condition previously accepted
any `persistentBrowser.mode != "always"`, which a missing/empty/disabled
value also satisfies — no evidence persistence is actually prohibited.
Tightened to require `persistentBrowser.mode == "never"` exactly. Added two
new test cases (missing/disabled control, and present-but-empty-mode) beyond
the existing "always" failure case.

## F-002 (medium) — ISSUE-0018 incorrectly records an unaccepted residual risk as accepted

Confirmed and fixed. `ISSUE-0018`'s "Out of scope" section called the
custom-authentication-strength limitation "an accepted MVP limitation,"
contradicting `ROADMAP.md`'s own `RISK-012` entry, which correctly says it
still needs the human's explicit treatment decision before v6 approval.
Reworded to "proposed... not yet an accepted residual" and made the issue's
own start conditional on that decision being recorded.

## F-003 (low) — Per-issue regression criteria use impossible existing-rule counts

Confirmed and fixed. `ISSUE-0015` and `ISSUE-0017` both said "14 other rules"
regardless of how many rules would actually pre-exist at each issue's own
implementation point (10 rules exist today; only 14 after all four M4 issues
land). Replaced with "any pre-existing rule" / an explicit count caveat
rather than a fixed, wrong number.

## F-004 (low, advisory, non-blocking) — M4 summary inaccurately says every proposed rule uses currently dropped fields

Confirmed and fixed anyway, though non-blocking. `ROADMAP.md`'s M4 milestone
row and issue-sequence preamble both said all four rules need previously
dropped fields; `ISSUE-0015`'s `location-restriction-present` in fact needs
no `normalize_policy` change at all (`includeLocations`/`excludeLocations`
are already captured). Reworded both passages to distinguish `ISSUE-0015`
from the other three.

## Governance-validator limitation noted by the reviewer

The reviewer's own sandbox could not run `python3 scripts/validate_repo.py`
(no writable temp directory in that read-only environment) — the same
structural review-sandbox limitation this project has documented and
accepted at every prior milestone/plan gate (M1 through M3, roadmap v3–v5).
Out-of-band evidence: `python3 scripts/validate_repo.py` passes (67 required
files checked) outside the review sandbox, at this exact commit, both before
and after this round's fixes.

## Summary

All three REQUIRED findings and the one ADVISORY are addressed at this
commit. This was the **second and final permitted planning-repair round**
(`AGENTS.md`: "at most two revision rounds before unresolved disagreement is
presented neutrally to the human") — round 1 reviewed `bb4952d6e6cc…`, round
2 reviewed `68655cc7b1e0…`, both `CHANGES_REQUIRED`. Per that limit, **no
further automated Codex plan review will be run against the fixes in this
commit** without the human's explicit direction to exceed the two-round
budget — the same disposition `DECISION-015` (v4) and `DECISION-029` (v5)
each used at their own revision-round caps. This record, the fixes above,
and the two rounds' full reports are presented directly for the human's
roadmap v6 decision: approve directly from this record, authorize a third
review round outside the normal budget, or reject/hold.

