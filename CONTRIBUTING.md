# Contributing

Contributions should keep this skeleton small, provider-native, understandable from a clean checkout, and useful without paid CI calls.

## Before changing the repository

1. Read [`START_HERE.md`](START_HERE.md), [`AGENTS.md`](AGENTS.md), and [`docs/workflow.md`](docs/workflow.md).
2. Open or identify an issue with bounded scope and acceptance criteria.
3. Create a focused branch such as `docs/clearer-onboarding` or `fix/review-launcher-validation`.
4. Do not include credentials, provider transcripts, local configuration, or unrelated generated files.

## Required checks

Run:

```sh
python3 scripts/validate_repo.py
git diff --check
```

When behavior changes, update the instructions, prompts, templates, and security limitations in the same contribution. A model's statement that checks passed is not evidence; record the command and real result.

## Pull requests

Use [the pull-request template](.github/PULL_REQUEST_TEMPLATE.md). Keep changes reviewable, name any AI assistance used, and identify the exact commit reviewed. The author may self-review, but an independent review must not reuse the author's conclusions as its own evidence.

Security reports follow [`SECURITY.md`](SECURITY.md), not the public issue tracker.
