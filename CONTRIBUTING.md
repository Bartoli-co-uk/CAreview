# Contributing

CAreview stays small, standard-library-only, understandable from a clean
checkout, and verifiable without paid CI calls. Contributions should preserve
those properties.

Two hard constraints, both recorded project requirements:

- **No third-party runtime dependencies and no Node.js toolchain.** Adding either
  needs a separate, approved decision, not a pull request.
- **No secrets, tenant data, or policy exports** in code, tests, fixtures,
  issues, or logs. Test fixtures use fake GUIDs.

## Before changing the repository

1. Read [`START_HERE.md`](START_HERE.md), [`AGENTS.md`](AGENTS.md), and
   [`docs/workflow.md`](docs/workflow.md).
2. Check [`project/status/CURRENT.md`](project/status/CURRENT.md) for the current
   stage and what is currently permitted.
3. Open or identify an issue with bounded scope and acceptance criteria.
4. Create a focused branch such as `docs/clearer-onboarding` or
   `fix/review-launcher-validation`.
5. Do not include credentials, provider transcripts, local configuration, or
   unrelated generated files.

## How changes get reviewed

This repository is built under a governed Claude + Codex workflow: Claude plans
and implements, a fresh read-only Codex process reviews each candidate commit,
and the repository owner approves each gate. If you are working as an AI agent
in this repository, that workflow is mandatory and is described in
[`docs/workflow.md`](docs/workflow.md).

Human contributors are not required to run the agent workflow, but the same
principles apply: bounded scope, real evidence, and documentation updated in the
same change as the behaviour.

## Required checks

Run all four and record the real output:

```sh
python3 -m unittest discover -s tests          # application tests
python3 -m py_compile $(git ls-files '*.py')   # compile check
python3 scripts/validate_repo.py               # required files, links, governance language
git diff --check                               # whitespace
```

CI runs the first three of these on every push and pull request, plus a
PowerShell syntax check of the review launcher, so a local pass should mean a
green build.

### If you touch the UI

The UI lives in `frontend/` (React + TypeScript, built with Vite). It is the
one documented exception to this project's stdlib-only, no-build-step rule —
see [DECISION-024](project/decisions/DECISION-024-react-frontend-build-step.md)
for its exact bounds. It needs Node.js/npm and two more checks:

```sh
cd frontend && npm install && npm run build     # compiles into web/index.html, index.js, index.css
cd frontend && npm test                         # Vitest suite
```

Two things to know before you start:

- **The build step is not optional.** `web/index.html`, `index.js`, and
  `index.css` are generated and gitignored, so a fresh clone serves no UI at
  all until you have run `npm run build`. `python3 server.py` will start
  happily and then 404 its own static routes.
- **CI does not run either of these yet.** The Python checks above are the
  whole of CI today, so nothing catches a broken frontend build or a failing
  Vitest test except you, locally, before you push. Wiring this up is tracked
  as `ISSUE-0014` in [`ROADMAP.md`](ROADMAP.md); until it lands, please run
  both and paste the real output into your pull request.

Do not add a third-party dependency to the Python backend, and do not expand
the Node toolchain beyond what `DECISION-024` already covers, without a
separate approved decision.

When behaviour changes, update the tests, documentation, prompts, templates, and
security limitations in the same contribution. A model's statement that checks
passed is not evidence; record the command and its real result.

Note that `scripts/validate_repo.py` enforces that certain governance phrases
survive somewhere in the Markdown corpus, and that every relative Markdown link
and heading anchor resolves. If it fails after a docs edit, that is usually why.

## Pull requests

Use [the pull-request template](.github/PULL_REQUEST_TEMPLATE.md). Keep changes
reviewable, name any AI assistance used, and identify the exact commit reviewed.
The author may self-review, but an independent review must not reuse the
author's conclusions as its own evidence.

Security reports follow [`SECURITY.md`](SECURITY.md), not the public issue
tracker.
