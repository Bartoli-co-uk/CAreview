# Issues

Create exactly one file per approved roadmap issue:

```text
project/issues/<ISSUE-ID>.md
```

For example, `project/issues/ISSUE-0001.md`. Copy
`project/templates/work-item.md` and replace every placeholder. The deterministic
review launcher requires this exact path and ID; put a human-readable slug on the
branch, not in the issue filename.

Work on one issue at a time. Record its roadmap binding, dependencies, allowed
paths, acceptance criteria, required checks, documentation, security impact,
implementation SHA, each Codex review round, and final decision.

The issue is not permission to expand scope or perform a protected action. It is
complete only after the mandatory fresh Codex review loop passes, required human
decisions are recorded, and `project/status/CURRENT.md` is updated.
