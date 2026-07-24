# Reviews

Store exact independent review output here, grouped by plan, issue, and
milestone. Filenames should include the subject, reviewed short SHA, provider,
and review type.

Example: `issues/ISSUE-0001-a1b2c3d4e5f6-codex.json`. Automated Codex reports
are schema-validated JSON envelopes; manually prepared Claude reports use the
Markdown templates under `project/templates/`.

Reviewers do not edit product files. The review launcher first stages its exact
validated JSON under `.git/claudex/reviews/`; copy it here unchanged and commit
it as workflow metadata. Any subsequent source change invalidates the earlier
review for approval purposes.

For milestone blindness, Claude reports must likewise remain outside the
candidate worktree. Only after all four blind reviews finish should their exact
outputs be copied here and committed. Every report names the reviewed candidate
SHA; the later metadata commit is not itself the candidate.
