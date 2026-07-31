# ISSUE-0017: Analyzer rule — admin-scoped sign-in frequency / no persistent browser

**Status:** `COMPLETE` (merged, with an accepted sandbox execution-evidence
residual) — the human reviewed the round-2 `BLOCKED` outcome (no
product-code defect; see round history below) and chose to accept the
residual, authorize the metadata-only `ROADMAP.md`/`README.md` follow-up,
and merge (`DECISION-042`)
**Milestone:** `M4` — bound by roadmap v6 (analyzer rule-set expansion); `M4` itself is `PLANNED`, not started
**Approved roadmap:** `ROADMAP.md` version `6`, `APPROVED` (`DECISION-034`, binds `68655cc7b1e0a63db3d6b37debf834c126bb60e0`) — binds this issue to `M4`
**Start authorization:** `DECISION-041`
**Dependencies:** `None` (independent of `ISSUE-0015`/`ISSUE-0016`; sequenced after them as the third `M4` issue delivered)
**Branch:** `ai/ISSUE-0017-admin-signin-frequency-rule`
**Starting SHA:** `48129547a68239e8f733ce6b50b6a63407a35256`
**Candidate SHA:** this commit — the launcher records the full HEAD SHA at review time; see the round table below for each round's exact reviewed SHA

## Objective

Add a new analyzer rule, `admin-signin-frequency`, that checks whether every
built-in admin role (`rules.ADMIN_ROLE_TEMPLATE_IDS`) is covered by an
enabled policy requiring short, periodic re-authentication with no
persistent browser session — matching CIS Microsoft 365 Foundations
Benchmark guidance for privileged-role sessions. Requires two additive
`graph.normalize_policy` fields for data Microsoft Graph already returns on
the same `identity/conditionalAccess/policies` call CAreview already makes.

## In scope

- `graph.py` — `normalize_policy`: add two new top-level keys,
  `signInFrequency` (`{"enabled": bool, "type": "days"|"hours"|"",
  "value": int|None, "frequencyInterval": "timeBased"|"everyTime"|""}`, read
  from `sessionControls.signInFrequency`) and `persistentBrowser`
  (`{"enabled": bool, "mode": "always"|"never"|""}`, read from
  `sessionControls.persistentBrowser`). Both default safely on
  missing/malformed input, following the file's existing pattern (never
  raises). Must not change the existing `sessionControls` key's current
  shape or its test contract (still `[]` on malformed input).
- `rules.py` — new `Rule("admin-signin-frequency", ...)`, medium severity,
  weight 10, plus a `_check_admin_signin_frequency` function using the
  **effective-coverage algorithm** below (deliberately more precise than
  `_check_mfa_for_admins`'s existing pattern, which ignores `excludeRoles`
  and doesn't handle an `includeUsers: ["All"]` policy contributing role
  coverage — Codex's round-1 plan review, F-004, flagged that copying it
  verbatim would carry the same ambiguity into this new rule; the existing,
  already-accepted `mfa-admins` rule itself is unchanged by this issue):

  1. **Qualifying policies**: enabled policies where `signInFrequency.enabled`
     is true with either `frequencyInterval == "everyTime"` or (`type ==
     "hours"` and `1 <= value <= 4` — human-confirmed threshold), AND
     `persistentBrowser.mode == "never"` **exactly** — not merely
     `!= "always"` (Codex's round-2 plan review, F-001: the rule's own stated
     requirement is "no persistent browser session," and a missing/disabled/
     empty-string `persistentBrowser.mode` is not evidence that persistence
     is prohibited, only that it wasn't configured either way). A day-scale
     interval, a disabled/missing `signInFrequency`, or any
     `persistentBrowser.mode` other than exactly `"never"` (including
     `"always"`, empty, or absent) all disqualify a policy, even if some
     other part of it looks compliant.
  2. **Effectively covered roles, per qualifying policy**: if `"All"` is in
     `includeUsers`, the policy covers `ADMIN_ROLE_TEMPLATE_IDS` **minus**
     any of those role IDs present in `excludeRoles` (an all-users policy
     that excludes a specific admin role does not cover that role).
     Otherwise, the policy covers `(includeRoles ∩ ADMIN_ROLE_TEMPLATE_IDS)
     minus excludeRoles`.
  3. **PASS** iff the union of effectively-covered-roles across *all*
     qualifying policies equals `ADMIN_ROLE_TEMPLATE_IDS`. Non-qualifying
     policies (e.g. admin-scoped but with too-long a frequency) are simply
     excluded from the union — they never subtract from or block coverage
     a qualifying policy already established for the same role; this is
     the direct fix for F-004's "overlapping compliant/non-compliant
     policies" ambiguity.
- `README.md` — one new "What it checks" table row; update rule-count/total-
  weight sentence.
- `tests/test_graph.py` — extend the missing-fields/malformed-nested-objects
  tests for the two new keys' safe defaults, plus one positive-shape test.
- `tests/test_analyzer.py` — at least nine cases: (1) admin-scoped enabled
  policy with `signInFrequency` disabled → FAIL; (2) same policy with
  `signInFrequency` enabled at `frequencyInterval: "everyTime"` (or 1–4
  hours) and `persistentBrowser.mode: "never"`, full admin-role union → PASS;
  (3) same as (2) but `persistentBrowser.mode: "always"` → still FAIL;
  (3a) same as (2) but `persistentBrowser` entirely absent/disabled → still
  FAIL; (3b) same as (2) but `persistentBrowser.mode: ""` (present but no
  mode set) → still FAIL — (3), (3a), and (3b) together prove
  `mode == "never"` is required exactly, not merely "not always" (Codex's
  round-2 plan review, F-001); (4) a qualifying `includeUsers: ["All"]`
  policy that also `excludeRoles` one admin role, with no other policy
  covering that role → FAIL (proves the all-users-minus-exclusion
  computation); (5) a qualifying policy covering all admin roles, PLUS a
  second, non-qualifying policy (frequency disabled) also scoped to one of
  those roles → still PASS (proves a non-qualifying overlapping policy
  doesn't subtract established coverage);
  (6) two qualifying policies whose role sets only jointly cover
  `ADMIN_ROLE_TEMPLATE_IDS` (neither alone does) → PASS (proves the union,
  not a single-policy check).
- `tests/fixtures/strong_tenant.json` — one new, narrowly-scoped additive
  policy entry satisfying this rule without perturbing any pre-existing
  rule's pass/fail state (12 rules will pre-exist at this issue's baseline,
  assuming `ISSUE-0015` and `ISSUE-0016` land first per the sequencing
  above — the exact count is whatever `rules.RULES` holds at the actual
  implementation baseline, not a number fixed by this document).

## Out of scope

- Any threshold other than the human-confirmed one above (`everyTime` or
  1–4 hours; day-scale intervals always fail) — a different threshold would
  need its own human decision, not a silent choice during implementation.
- The other three proposed rules (`location-restriction-present`,
  `terms-of-use-required`, `phishing-resistant-mfa-admins`) — each is its
  own issue.

## Allowed paths

- `graph.py`, `rules.py`, `README.md`, `tests/test_graph.py`,
  `tests/test_analyzer.py`, `tests/fixtures/strong_tenant.json`

## Acceptance criteria

1. `python3 -m unittest discover -s tests` passes, including the new
   `test_graph.py` cases and all nine `admin-signin-frequency` analyzer
   cases.
2. `normalize_policy({})` gains exactly the two new top-level keys described
   above, both safely defaulted; no existing normalized field is removed,
   renamed, or reshaped.
3. The rule implements the effective-coverage algorithm exactly as specified
   (role coverage computed per qualifying policy, including the
   all-users-minus-`excludeRoles` case; union across qualifying policies
   only; non-qualifying policies never subtract established coverage) —
   not a single narrow-policy check, and not a verbatim copy of
   `mfa-admins`'s simpler pattern.
4. `README.md`'s "What it checks" table and rule-count/total-weight sentence
   match `rules.py` exactly.
5. `test_strong_tenant_scores_high` (or equivalent) continues to expect a
   full pass at the new total weight after the one new fixture policy is
   added; no other rule's pass/fail state on any fixture changes.

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass, deterministic scores |
| Governance | `python3 scripts/validate_repo.py` | passes |

## Documentation

- `README.md`: new "What it checks" table row; updated rule-count/weight
  sentence in the same section. The rule's rationale text should state the
  exact threshold (everyTime or 1–4 hours) so a reader can reproduce the
  pass/fail decision from the tenant's own policy configuration.

## Security and privacy impact

- Threat-model delta: none — reads fields already present in the same
  already-fetched, already in-memory Graph response; no new Graph call,
  scope, or permission.
- Data/secret impact: none.
- Dependency/supply-chain impact: none; standard library only.
- Protected actions: none.

## Stop conditions

- Any change to the human-confirmed threshold without going back for a
  fresh human decision.
- Any fixture change that perturbs an existing rule's pass/fail state — if
  unavoidable, stop and re-scope rather than silently accepting a
  fixture-driven regression elsewhere.
- Any weakening of the full-admin-role-union coverage requirement to a
  single-policy check (would reopen the same gap Codex previously flagged
  for `mfa-admins`, historically tracked as F-003).

## Round history

| Round | Reviewed SHA | Outcome | Findings |
|---|---|---|---|
| 0 | `079f5c72cb27c2e525b59d70c6bc5e3d0ee9a7f6` | `CHANGES_REQUIRED` | F-001 (medium, real defect): `_qualifies_for_admin_signin_frequency` checked only `persistentBrowser.mode == "never"`, ignoring `persistentBrowser.enabled` — a disabled control with a stale `mode: "never"` falsely qualified. Fixed in round 1: both `enabled is True` and `mode == "never"` are now required, with a new regression test. |
| 1 | `72910d8b22dd74d664036d74c0d909e1d6a32c6a` | `BLOCKED` | F-001 (medium, sandbox-only: same accepted execution-evidence limitation class as prior issues). F-002 (medium, real: issue/handoff records left internally contradictory after the round-1 source fix — candidate-SHA header and handoff primary sections still round-0-shaped). Both fixed in round 2 (record accuracy only; no further source change). |
| 2 | `2a55a56ce2551260102104c3718429f8ce6b2e62` | `BLOCKED` | F-001 (medium, sandbox-only: same accepted class). F-002 (medium, real, **unresolved**: `ROADMAP.md`'s `M4` status/delivery-status prose was never updated past the round-0 commit — it still says only the round-0 candidate exists and its initial review is awaited, though rounds 1-2 had already landed). F-003 (low, advisory, pre-existing, unrelated to this issue's own changes: `README.md`'s usage-section prose says "188 Python unit tests," now 18 behind the true count). No product-code defect at any round. |

This was the second and final permitted issue repair round (`AGENTS.md`); no
third repair may be attempted regardless of finding severity. Per that
bounded-repair rule, this Claude task stops here and presents the findings
to the human — see "Human decision required" below.

## Human decision required

Round 2's remaining findings, none of which are a product-code defect:

- **F-001** (medium, sandbox-only): the review sandbox cannot independently
  complete `python3 -m py_compile`, the full `unittest discover` run, or
  `scripts/validate_repo.py` (denied bytecode writes, loopback sockets, and
  a writable temp directory respectively). This is the same accepted
  execution-evidence limitation class as `ISSUE-0014` (`DECISION-031`),
  `ISSUE-0015` (`DECISION-037`), and `ISSUE-0016` (`DECISION-040`). All
  three checks were independently run in this task's own environment at
  every round with real passing results (206 tests, compile exit 0,
  governance validation passed — see the handoff's round tables).
- **F-002** (medium, real, unresolved): `ROADMAP.md`'s `M4` delivery-status
  prose (two locations, lines 14 and 27) was updated once, in the initial
  round-0 commit, to say `ISSUE-0017` is `IN PROGRESS` and its round-0
  review is awaited — but was never touched again in rounds 1 or 2, so it
  now understates the true state (two repair rounds have landed, the
  budget is exhausted, and this round's own review is what surfaced the
  gap). No repair round remains to fix it directly.
- **F-003** (low, advisory, pre-existing): `README.md`'s usage-section
  prose says "188 Python unit tests" — stale independent of this issue
  (the count was already behind before `ISSUE-0017` started; this issue's
  own "What it checks" table/weight sentence, the one README section its
  own acceptance criteria govern, is correct and current).

**Options for the human:**
1. **Accept F-001 as the same residual class already accepted for
   `ISSUE-0014`/`ISSUE-0015`/`ISSUE-0016`**, authorize a follow-up,
   metadata-only commit to fix `ROADMAP.md` (F-002) and, optionally,
   `README.md`'s stale count (F-003), and authorize merging
   `ai/ISSUE-0017-admin-signin-frequency-rule` to `main` — the same
   disposition `DECISION-037`/`DECISION-040` gave the equivalent residual
   for `ISSUE-0015`/`ISSUE-0016`. A metadata-only commit does not itself
   need a fresh Codex review (no product source changes), consistent with
   `AGENTS.md`'s "metadata-only report/status update... does not make the
   metadata commit itself reviewed" language — it is corrective record
   hygiene, not a new implementation round.
2. **Decline to merge** and instead direct a different disposition (e.g.
   hold the branch, request a different scope for the follow-up fix, or
   re-open a fresh issue-scoped task with its own new repair budget rather
   than a same-task metadata commit).
3. **Ask for something else** — e.g. an independent re-run of the three
   required checks in a different environment before deciding.

## Advance/merge decision

The human reviewed round 2's `BLOCKED` outcome (no product-code defect)
and the real, independently-run check results and chose option 1: accept
the sandbox execution-evidence residual, authorize the metadata-only
`ROADMAP.md` (F-002) and `README.md` (F-003) follow-up, and merge — the
same disposition used repeatedly for this class of finding elsewhere in
this project (most recently `ISSUE-0016`, `DECISION-040`). `DECISION-042`
records the exact binding. `ai/ISSUE-0017-admin-signin-frequency-rule` is
merged to `main`.
