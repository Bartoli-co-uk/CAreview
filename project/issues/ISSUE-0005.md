# ISSUE-0005: UI rendering — score, findings, and policy flow cards

**Status:** `REVIEWING`
**Milestone:** `M1`
**Approved roadmap:** `ROADMAP.md` version `3` at `125d74f6d4bfe85f1a727293064d0887f2d121c7`
**Dependencies:** `ISSUE-0003`, `ISSUE-0004`
**Branch:** `ai/ISSUE-0005-ui-rendering`
**Starting SHA:** `67283f7e4a499af5e813a3f7d325bc81f9ddace8`
**Candidate SHA:** `this commit (branch HEAD); launcher binds the exact SHA`

## Objective

Render the analysis in the local UI: a 0–100 score gauge, a severity-sorted
findings list, and a simple per-policy flow card
(Users → Conditions → Apps → Controls), wired to the API.

## In scope

- `web/app.js`, `web/index.html`, `web/style.css` — fetch `/api/policies` and
  `/api/analysis`, render score, findings, and one card per policy; show clear
  states for signed-out, loading, error/consent, and empty.
- A review-only fixture path so the UI can render offline against sample data
  without signing in (e.g. a `/api/analysis?sample=1` guarded local shortcut, or
  a committed sample JSON the page can load).

## Out of scope

- New analysis rules or Graph fields (earlier issues).
- Exports, persona/CIS views (non-goals).

## Allowed paths

- `web/**`, `server.py` (only a local, non-sensitive sample endpoint if used),
  `tests/**`

## Acceptance criteria

1. After sign-in and fetch, the page shows the score, findings, and per-policy
   cards with no console errors.
2. Findings render severity-sorted with each rule's rationale/remediation.
3. Signed-out, loading, empty, and consent-error states are handled visibly.
4. The UI renders correctly offline against the sample/fixture path for review.
5. The score is visibly labeled a heuristic (RISK-004).
6. **Untrusted-content safety (Codex F-005):** all tenant-supplied and finding
   strings are inserted as text (e.g. `textContent`), never as HTML; no
   `innerHTML`/`eval`/dynamic code with untrusted data; a test/fixture containing
   a policy display name with markup (e.g. `<img onerror>`), quotes, and
   angle-brackets renders inertly.
7. The page sets a **restrictive Content-Security-Policy** (no external origins;
   no inline event handlers) and the server sends **`Cache-Control: no-store`** on
   sensitive API responses (`/api/policies`, `/api/analysis`).

## Required checks

| Check | Command or method | Expected result |
|---|---|---|
| Compile | `python3 -m py_compile $(git ls-files '*.py')` | exit 0 |
| Tests | `python3 -m unittest discover -s tests` | all pass |
| Manual render | Load page with sample path, then a live run | score/findings/cards render; no console errors |

## Documentation

- README: a short "what you'll see" note and the offline sample path.

## Security and privacy impact

- Threat-model delta: none new; renders already-local data.
- Data/secret impact: any sample data committed must be sanitized; never render
  or log tokens. Tenant policy strings are untrusted input and must be rendered
  as inert text (Codex F-005).
- Dependency/supply-chain impact: none; no external scripts/styles/fonts — all
  assets are local, enforced by a restrictive CSP.
- Protected actions: none.

## Stop conditions

- Any need to load an external script/style/font, or to commit real tenant data
  as a sample.

## Implementation and review rounds

| Round | Claude handoff | Candidate SHA | Check evidence | Fresh Codex report | Outcome |
|---:|---|---|---|---|---|
| 0 | `[path]` | `[SHA]` | `[path/summary]` | `[path]` | `[outcome]` |

Maximum two repair rounds; every Codex review is a fresh ephemeral read-only
process against the named SHA.

## Completion

- Final reviewed product SHA: `[SHA]`
- Human advance/merge decision: `[path]`
- Merge/result SHA: `[SHA or N/A]`
- Residual risks or follow-up: `[list]`
- Status record updated: `[commit/path]`
