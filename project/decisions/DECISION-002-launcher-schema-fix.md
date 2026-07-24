# Human decision: Fix Codex review-launcher schema bug

**Decision ID:** `DECISION-002`
**Type:** `protected action (agent-configuration / governance script change)`
**Decision:** `APPROVE`
**Human approver:** `Jay (@Jay-cli), repository owner`
**Decided at:** `2026-07-24T10:45:00Z`

## Exact binding

- Artifact/action: edit `scripts/run_codex_review.py`, function `provider_compatible_schema`
- Target: `Bartoli-co-uk/CAreview` working copy
- Scope: add a branch that treats the JSON-Schema `properties` map as a
  name→subschema mapping (recurse into values, preserve names) instead of
  passing property names through the keyword allow-list.
- Exclusions: no other launcher behaviour, gate logic, model tiering, or security
  floor is changed. Upstream `ClaudexCodexSetUp` is not modified by this decision.
- Expiry/review date: `N/A`

## Decision text

> Approval question "The ClaudexCodexSetUp Codex-review launcher has a schema bug
> that blocks every real Codex review… how do you want to proceed?" —
> answered "Apply the fix to CAreview now".

## Evidence shown to the human

- Reproduction: real `codex exec --output-schema` returned
  `invalid_json_schema: 'required' is required … to be an array`; the generated
  provider schema was `{"type":"object","additionalProperties":false,
  "required":[…10 fields…],"properties":{}}` — an unsatisfiable schema.
- Root cause: `provider_compatible_schema` recursed into the `properties` dict and
  dropped every entry because property names are not schema keywords.
- Verified fix: with the corrected transform, `codex exec` returned exit 0 and a
  valid schema-conforming report.
- CI never caught this: the validator's launcher smoke tests use a mock `codex`
  that ignores `--output-schema`.

## Consequence

- Permitted next action: re-run `./scripts/run-codex-review.sh plan <SHA>` and
  continue the workflow's normal gates.
- Invalidated approvals/reviews: none (no prior real Codex review existed).
- Rollback/recovery expectation: revert the single-function change if it ever
  causes a schema regression; the previous behaviour produced no valid reviews.

## Notes

The change **enables** the review gate (previously non-functional) and does not
weaken it: it makes the output schema valid so Codex can produce a schema-bound
report. It applies equally to plan, issue, and both milestone/security modes.

Known follow-ups (not part of this decision):
- The same bug exists upstream in `Bartoli-co-uk/ClaudexCodexSetUp` and should be
  fixed there separately so future projects inherit the correction.
- `scripts/validate_repo.py`'s wrong-stage smoke test has a latent bug: it assumes
  the repository is never legitimately at `stage: ROADMAP_REVIEW`, so the
  validator reports one error while a plan review is staged. Non-blocking; to be
  raised separately.
