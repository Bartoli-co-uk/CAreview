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
