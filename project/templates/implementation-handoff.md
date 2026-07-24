# Claude handoff: ISSUE-[NNNN], round [0]

**Claude issue task:** `[identifier]`
**Approved issue:** `[path and commit SHA]`
**Starting SHA:** `[SHA]`
**Candidate SHA:** `[SHA]`
**Created at:** `[UTC timestamp]`

## Outcome

[What was implemented or why work stopped.]

## Changed files

| Path | Change and reason |
|---|---|
| `[path]` | `[description]` |

## Decisions and assumptions

- `[Decision, evidence, and consequence]`

## Acceptance-criteria mapping

| Criterion | Implementation evidence | Status |
|---|---|---|
| `[criterion]` | `[path/test]` | `[met/not met]` |

## Verification requested and observed

| Check | Exact command | Actual result/exit | Evidence limitation |
|---|---|---|---|
| `[check]` | `[command]` | `[result]` | `[limitation]` |

The reviewer or CI must independently confirm required checks; this handoff is not test authority.

## Documentation

- `[Updated file and behaviour documented]`

## Security and residual risk

- Threat-model change: `[description]`
- Residual risk/uncertainty: `[description]`
- Protected action attempted: `[No / stop details]`

## Review request

- Base SHA: `[SHA]`
- Head SHA: `[SHA]`
- Review command: `./scripts/run-codex-review.sh issue ISSUE-[NNNN] [BASE-SHA] [HEAD-SHA]`
- PowerShell: `.\scripts\run-codex-review.ps1 issue ISSUE-[NNNN] [BASE-SHA] [HEAD-SHA]`
- Areas needing special attention: `[list]`
