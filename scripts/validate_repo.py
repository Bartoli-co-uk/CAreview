#!/usr/bin/env python3
"""Validate the lean Claude + Codex repository skeleton with the stdlib only."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11: TOML validation is skipped explicitly.
    tomllib = None


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = (
    "README.md", "START_HERE.md", "AGENTS.md", "CLAUDE.md", "ROADMAP.md", "LICENSE",
    "SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SUPPORT.md", ".gitignore",
    ".gitattributes", ".editorconfig",
    ".claude/settings.json", ".claude/agents/requirements-planner.md",
    ".claude/agents/implementation-author.md", ".claude/agents/milestone-reviewer.md",
    ".claude/agents/security-reviewer.md", ".claude/agents/docs-scribe.md",
    ".claude/agents/status-scribe.md", ".claude/rules/workflow.md",
    ".claude/rules/review-boundaries.md", ".claude/rules/safety.md", ".codex/config.toml",
    ".codex/agents/plan-reviewer.toml", ".codex/agents/issue-reviewer.toml",
    ".codex/agents/milestone-reviewer.toml", ".codex/agents/security-reviewer.toml",
    ".github/CODEOWNERS", ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/defect.yml", ".github/ISSUE_TEMPLATE/implementation.yml",
    ".github/ISSUE_TEMPLATE/project-clarification.yml", ".github/ISSUE_TEMPLATE/security-remediation.yml",
    ".github/workflows/validate.yml", "docs/workflow.md", "docs/roles-and-responsibilities.md",
    "docs/approvals-and-reviews.md", "docs/security-boundaries.md", "docs/model-assignment.md",
    "prompts/README.md",
    "prompts/01-project-brief.md", "prompts/02-roadmap.md", "prompts/03-codex-plan-review.md",
    "prompts/04-implement-issue.md", "prompts/05-codex-issue-review.md", "prompts/06-repair-issue.md",
    "prompts/07-milestone-general-review.md", "prompts/08-milestone-security-review.md", "project/README.md",
    "project/intake/PROJECT_DESCRIPTION.md", "project/status/CURRENT.md", "project/templates/project-brief.md",
    "project/templates/roadmap.md", "project/templates/work-item.md", "project/templates/implementation-plan.md",
    "project/templates/implementation-handoff.md", "project/templates/review.md",
    "project/templates/security-review.md", "project/templates/milestone.md", "project/templates/decision.md",
    "project/templates/risk-acceptance.md", "scripts/run-codex-review.sh", "scripts/run-codex-review.ps1",
    "scripts/run_codex_review.py", "scripts/validate_repo.py",
)

# Each phrase is a lower-cased substring that must survive somewhere in the
# Markdown corpus. This is a deliberately coarse guard that the core governance
# language has not been silently deleted; it is not a semantic check, so reword
# a governed rule and its phrase together, and keep phrases distinctive.
KEY_PHRASES = {
    "brief approval gate": "brief approval",
    "roadmap approval gate": "roadmap approval",
    "implementation prohibition": "no implementation begins until",
    "sequential issues": "one issue at a time",
    "fresh top-level issue task": "new top-level claude task",
    "no issue-session reuse": "do not resume, continue, or fork",
    "Claude general milestone review": "claude full general review",
    "Codex general milestone review": "codex full general review",
    "Claude security milestone review": "claude security review",
    "Codex security milestone review": "codex security review",
    "same milestone target": "same commit",
    "all-four milestone repair invalidation": "reruns all four",
    "bounded repairs": "at most two repair rounds",
    "durable status": "project/status/current.md",
    "provider deletion limitation": "does not delete provider-side records",
    "launcher fail-closed exit": "codex unavailable, unauthenticated, or execution failed",
    "security model floor": "must not downgrade a security review",
}

LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def all_files(suffix: str) -> list[Path]:
    return sorted(
        path for path in ROOT.rglob(f"*{suffix}")
        if ".git" not in path.relative_to(ROOT).parts and path.is_file()
    )


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker = match.group(1)[0]
            fence = marker if fence is None else (None if marker == fence else fence)
            output.append("")
        else:
            output.append(line if fence is None else "")
    return "\n".join(output)


def heading_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in strip_fenced_code(path.read_text(encoding="utf-8")).splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        heading = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", match.group(2))
        heading = re.sub(r"<[^>]+>", "", heading).replace("`", "").strip().lower()
        base = re.sub(r"\s+", "-", re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE))
        count = counts.get(base, 0)
        counts[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def validate_links(errors: list[str]) -> None:
    anchor_cache: dict[Path, set[str]] = {}
    root = ROOT.resolve()
    for source in all_files(".md"):
        for match in LINK_RE.finditer(strip_fenced_code(source.read_text(encoding="utf-8"))):
            raw = match.group(1).strip()
            raw = raw[1:raw.index(">")] if raw.startswith("<") and ">" in raw else raw.split(maxsplit=1)[0]
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc or raw.startswith("//"):
                continue
            path_text = unquote(parsed.path)
            target = source if not path_text else (ROOT / path_text.lstrip("/") if path_text.startswith("/") else source.parent / path_text)
            resolved = target.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{source.relative_to(ROOT)}: local link escapes repository: {raw}")
                continue
            if not resolved.exists():
                errors.append(f"{source.relative_to(ROOT)}: missing local link target: {raw}")
                continue
            fragment = unquote(parsed.fragment).lower()
            if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
                anchors = anchor_cache.setdefault(resolved, heading_anchors(resolved))
                if fragment not in anchors:
                    errors.append(f"{source.relative_to(ROOT)}: missing heading #{fragment} in {resolved.relative_to(ROOT)}")


def validate_formats(errors: list[str], notices: list[str]) -> None:
    for path in all_files(".json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
    if tomllib is None and all_files(".toml"):
        notices.append("TOML parsing skipped because Python 3.11+ tomllib is unavailable.")
    elif tomllib is not None:
        for path in all_files(".toml"):
            try:
                tomllib.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: invalid TOML: {exc}")


def validate_workflow(errors: list[str]) -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in all_files(".md")).lower()
    for label, phrase in KEY_PHRASES.items():
        if phrase not in corpus:
            errors.append(f"missing required workflow language for {label!r}: {phrase!r}")
    uses = re.compile(r"^\s*uses:\s*[^\s@]+@([^\s#]+)", re.MULTILINE)
    for path in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
        for reference in uses.findall(path.read_text(encoding="utf-8")):
            if not re.fullmatch(r"[0-9a-fA-F]{40}", reference):
                errors.append(f"{path.relative_to(ROOT)}: GitHub Action is not pinned to a full commit SHA: {reference}")
    state_text = (ROOT / "project/status/CURRENT.md").read_text(encoding="utf-8")
    state_match = re.match(
        r"\A<!-- claudex-state\n"
        r"stage: ([A-Z][A-Z0-9_]*)\n"
        r"active_issue: ([A-Za-z0-9_-]+|none)\n"
        r"active_milestone: ([A-Za-z0-9_-]+|none)\n"
        r"-->\n",
        state_text,
    )
    if state_text.count("<!-- claudex-state") != 1:
        errors.append("project/status/CURRENT.md must contain exactly one claudex-state block")
    elif not state_match:
        errors.append("project/status/CURRENT.md must begin with one canonical claudex-state block")
    else:
        stage, active_issue, active_milestone = state_match.groups()
        if stage in {"ISSUE_REVIEW", "ISSUE_REPAIR"} and active_issue == "none":
            errors.append(f"claudex-state {stage} requires an active_issue")
        if stage == "MILESTONE_REVIEW" and active_milestone == "none":
            errors.append("claudex-state MILESTONE_REVIEW requires an active_milestone")


def checked(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)


def initialize(root: Path) -> bool:
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.name", "Skeleton Validator"],
        ["git", "config", "user.email", "validator@example.invalid"],
    ):
        if checked(command, root).returncode:
            return False
    return True


def commit(root: Path, message: str) -> bool:
    return not any(
        checked(command, root).returncode
        for command in (
            ["git", "add", "."],
            ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", message],
        )
    )


def sha(root: Path) -> str:
    return checked(["git", "rev-parse", "HEAD"], root).stdout.strip()


def write_state(root: Path, stage: str, issue: str = "none", milestone: str = "none") -> None:
    path = root / "project/status/CURRENT.md"
    text = re.sub(
        r"\A<!-- claudex-state\n.*?\n-->\n", "", path.read_text(encoding="utf-8"), count=1, flags=re.DOTALL
    )
    block = (
        "<!-- claudex-state\n"
        f"stage: {stage}\nactive_issue: {issue}\nactive_milestone: {milestone}\n"
        "-->\n"
    )
    path.write_text(block + text, encoding="utf-8")


def create_mock(path: Path, outcome: str, malformed: bool = False) -> None:
    source = f'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import re
import subprocess
import sys

if sys.argv[1:] == ["--version"]:
    print("mock-codex 1.0")
    raise SystemExit(0)
args = sys.argv[1:]
if not args or args[0] != "exec" or "--output-last-message" not in args or "--output-schema" not in args:
    raise SystemExit(2)
if os.environ.get("CLAUDEX_VALIDATOR_SECRET"):
    raise SystemExit(4)
Path(__file__).with_suffix(".invoked").write_text("exec\\n", encoding="utf-8")
checkout = Path(args[args.index("--cd") + 1])
objects = subprocess.check_output(
    ["git", "-C", str(checkout), "cat-file", "--batch-all-objects", "--batch-check=%(objecttype) %(objectname)"],
    text=True,
)
prompt = sys.stdin.read()
mode = re.search(r"^Review mode: ([a-z-]+)$", prompt, re.MULTILINE).group(1)
target_id = re.search(r"^Target ID: (.*)$", prompt, re.MULTILINE).group(1)
base = re.search(r"^Base commit: (.*)$", prompt, re.MULTILINE).group(1)
head = re.search(r"^Target commit: ([0-9a-f]{{40}})$", prompt, re.MULTILINE).group(1)
if sum(line.startswith("commit ") for line in objects.splitlines()) != (2 if base else 1):
    raise SystemExit(3)
findings = []
if {outcome!r} in ("CHANGES_REQUIRED", "REMEDIATION_REQUIRED"):
    finding = {{
        "id": "F-TEST", "classification": "REQUIRED", "severity": "medium", "confidence": "high",
        "blocking": True, "title": "Seeded test finding", "locations": [{{"path": "ROADMAP.md", "line": 1}}],
        "evidence": ["Seeded validator evidence"], "remediation": "Repair the seeded condition",
        "verification": "Run the validator again",
    }}
    if mode == "milestone-security":
        finding.update({{
            "fingerprint": "seeded-security-fingerprint", "category": "test/security",
            "attack_preconditions": "A seeded precondition", "impact": "A seeded impact",
            "exploitability": "Seeded and bounded", "disposition": "open",
        }})
    findings = [finding]
report = {{
    "schema_version": "1.0", "mode": mode, "target_id": target_id, "base_sha": base,
    "reviewed_sha": head, "outcome": {outcome!r}, "summary": "Mock validator review",
    "findings": findings, "evidence": [{{"source": "file", "reference": "ROADMAP.md", "detail": "Mock evidence"}}],
    "limitations": [],
}}
if {malformed!r}:
    report["findings"] = [{{
        "id": "F-BAD", "classification": "BLOCKER", "severity": "high", "confidence": "high",
        "blocking": False, "title": "Invalid pass", "locations": [{{"path": "ROADMAP.md", "line": 1}}],
        "evidence": ["Bad semantics"], "remediation": "Fix", "verification": "Retest",
    }}]
Path(args[args.index("--output-last-message") + 1]).write_text(json.dumps(report), encoding="utf-8")
print(json.dumps({{"type": "thread.started", "thread_id": "mock-fresh-thread"}}))
print(json.dumps({{"type": "turn.completed"}}))
'''
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_provider(root: Path, mock: Path, *args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["CLAUDEX_VALIDATOR_SECRET"] = "must-not-reach-provider"
    return checked(
        ["sh", "scripts/run-codex-review.sh", "--test-provider", str(mock), *args], root, environment
    )


def load_test_reports(root: Path, category: str) -> list[dict[str, object]]:
    directory = root / ".git/claudex/test-reviews" / category
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))] if directory.is_dir() else []


def make_copy(temp_dir: str) -> Path:
    root = Path(temp_dir) / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    return root


def smoke_plan(errors: list[str], outcome: str) -> None:
    with tempfile.TemporaryDirectory(prefix="claudex-plan-validator-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, outcome)
        write_state(root, "ROADMAP_REVIEW")
        if not initialize(root) or not commit(root, "plan candidate"):
            errors.append("mock plan fixture could not initialize")
            return
        head = sha(root)
        result = test_provider(root, mock, "plan", head)
        reports = load_test_reports(root, "plans")
        if result.returncode != 78 or len(reports) != 1:
            errors.append(f"mock plan {outcome} did not complete as test-only evidence: {result.stderr.strip()}")
            return
        report = reports[0]
        review = report.get("review", {})
        if report.get("authoritative") is not False or report.get("test_only") is not True:
            errors.append("test provider report was not clearly marked non-authoritative")
        if not isinstance(review, dict) or review.get("outcome") != outcome or review.get("reviewed_sha") != head:
            errors.append(f"mock plan {outcome} report lost its target binding")
        if (root / ".git/claudex/reviews").exists():
            errors.append("test provider created an authoritative report directory")


def smoke_issue(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="claudex-issue-validator-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        if not initialize(root) or not commit(root, "issue base"):
            errors.append("mock issue fixture could not create base")
            return
        base = sha(root)
        write_state(root, "ISSUE_REVIEW", issue="ISSUE-TEST")
        (root / "project/issues/ISSUE-TEST.md").write_text(
            f"# ISSUE-TEST\n\n**Status:** `REVIEWING`  \n**Starting SHA:** `{base}`  \n", encoding="utf-8"
        )
        if not commit(root, "issue candidate"):
            errors.append("mock issue fixture could not create candidate")
            return
        head = sha(root)
        result = test_provider(root, mock, "issue", "ISSUE-TEST", base, head)
        reports = load_test_reports(root, "issues")
        review = reports[0].get("review", {}) if len(reports) == 1 else {}
        if result.returncode != 78 or not isinstance(review, dict) or review.get("base_sha") != base or review.get("reviewed_sha") != head:
            errors.append(f"mock issue review failed target binding or isolation: {result.stderr.strip()}")


def smoke_milestones(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="claudex-milestone-validator-") as temp_dir:
        root = make_copy(temp_dir)
        general_mock = Path(temp_dir) / "mock-codex-general"
        security_mock = Path(temp_dir) / "mock-codex-security"
        create_mock(general_mock, "PASS")
        create_mock(security_mock, "REMEDIATION_REQUIRED")
        write_state(root, "MILESTONE_REVIEW", milestone="M1")
        (root / "project/milestones/M1.md").write_text("# M1\n\n**Status:** `REVIEWING`  \n", encoding="utf-8")
        if not initialize(root) or not commit(root, "milestone candidate"):
            errors.append("mock milestone fixture could not initialize")
            return
        head = sha(root)
        general = test_provider(root, general_mock, "milestone-general", "M1", head)
        security = test_provider(root, security_mock, "milestone-security", "M1", head)
        if general.returncode != 78 or security.returncode != 78:
            errors.append(
                "mock milestone modes did not accept the same bound candidate: "
                f"general={general.returncode} security={security.returncode}"
            )
            return
        reports = load_test_reports(root, "milestones")
        status = checked(["git", "status", "--porcelain", "--untracked-files=all"], root)
        if len(reports) != 2 or status.stdout.strip() or (root / ".git/claudex/reviews").exists():
            errors.append("milestone test reviews did not remain outside the clean candidate worktree")
            return
        if any(report.get("metadata", {}).get("model") != "codex-cli-default" for report in reports):
            errors.append("launcher did not record the default Codex model in the review envelope")
        security_reviews = [
            report.get("review", {}) for report in reports
            if isinstance(report.get("review"), dict)
            and report["review"].get("mode") == "milestone-security"
        ]
        required_security_fields = {
            "fingerprint", "category", "attack_preconditions", "impact", "exploitability", "disposition"
        }
        if (
            len(security_reviews) != 1
            or security_reviews[0].get("outcome") != "REMEDIATION_REQUIRED"
            or not security_reviews[0].get("findings")
            or not required_security_fields.issubset(security_reviews[0]["findings"][0])
        ):
            errors.append("milestone security schema lost required finding fields")


def smoke_rejections(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="claudex-rejection-validator-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS", malformed=True)
        write_state(root, "ROADMAP_REVIEW")
        if not initialize(root) or not commit(root, "rejection candidate"):
            errors.append("launcher rejection fixture could not initialize")
            return
        head = sha(root)
        malformed = test_provider(root, mock, "plan", head)
        if malformed.returncode != 65 or load_test_reports(root, "plans"):
            errors.append("launcher staged semantically invalid structured output")

        env = os.environ.copy()
        env["CODEX_BIN"] = str(mock)
        override = checked([sys.executable, "scripts/run_codex_review.py", "plan", head], root, env)
        if override.returncode != 64:
            errors.append("production launcher did not reject the legacy CODEX_BIN override")

        if os.name != "nt":
            nested = root / "nested/path"
            nested.mkdir(parents=True)
            (nested / "unsafe-link").symlink_to("../../ROADMAP.md")
            if not commit(root, "nested unsafe symlink"):
                errors.append("nested-symlink fixture could not commit")
                return
            rejected = test_provider(root, mock, "plan", sha(root))
            if rejected.returncode != 64 or "unsupported symlink" not in rejected.stderr:
                errors.append("launcher did not reject a nested committed symlink before provider execution")
                return

            (nested / "unsafe-link").unlink()
            module = root / "vendor/module"
            module.mkdir(parents=True)
            if not initialize(module):
                errors.append("gitlink fixture could not initialize its nested repository")
                return
            (module / "README.md").write_text("fixture\n", encoding="utf-8")
            if not commit(module, "nested fixture"):
                errors.append("gitlink fixture could not commit its nested repository")
                return
            module_sha = sha(module)
            for command in (
                ["git", "add", "-u"],
                ["git", "update-index", "--add", "--cacheinfo", f"160000,{module_sha},vendor/module"],
                ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "unsafe gitlink"],
            ):
                if checked(command, root).returncode:
                    errors.append("gitlink rejection fixture could not commit")
                    return
            rejected = test_provider(root, mock, "plan", sha(root))
            if rejected.returncode != 64 or "unsupported gitlink" not in rejected.stderr:
                errors.append(
                    "launcher did not reject a committed gitlink before provider execution: "
                    f"exit {rejected.returncode}, {rejected.stderr.strip()}"
                )


def assert_preflight_rejected(
    errors: list[str], label: str, root: Path, mock: Path, *launcher_args: str
) -> None:
    marker = mock.with_suffix(".invoked")
    if marker.exists():
        marker.unlink()
    result = test_provider(root, mock, *launcher_args)
    report_root = root / ".git/claudex"
    staged = list(report_root.rglob("*.json")) if report_root.exists() else []
    if result.returncode != 64 or marker.exists() or staged:
        errors.append(
            f"{label} did not fail before provider execution/report staging: "
            f"exit {result.returncode}, marker={marker.exists()}, reports={len(staged)}, {result.stderr.strip()}"
        )


def smoke_target_binding_rejections(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="claudex-wrong-stage-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        if not initialize(root) or not commit(root, "wrong stage"):
            errors.append("wrong-stage fixture could not initialize")
        else:
            assert_preflight_rejected(errors, "wrong stage", root, mock, "plan", sha(root))

    with tempfile.TemporaryDirectory(prefix="claudex-wrong-issue-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        if not initialize(root) or not commit(root, "issue base"):
            errors.append("wrong-active-issue fixture could not create base")
        else:
            base = sha(root)
            write_state(root, "ISSUE_REVIEW", issue="ISSUE-OTHER")
            (root / "project/issues/ISSUE-TEST.md").write_text(
                f"# ISSUE-TEST\n\n**Status:** `REVIEWING`  \n**Starting SHA:** `{base}`  \n", encoding="utf-8"
            )
            if not commit(root, "wrong active issue"):
                errors.append("wrong-active-issue fixture could not create candidate")
            else:
                assert_preflight_rejected(
                    errors, "wrong active issue", root, mock, "issue", "ISSUE-TEST", base, sha(root)
                )

    with tempfile.TemporaryDirectory(prefix="claudex-wrong-base-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        if not initialize(root) or not commit(root, "issue base"):
            errors.append("wrong-starting-SHA fixture could not create base")
        else:
            base = sha(root)
            write_state(root, "ISSUE_REVIEW", issue="ISSUE-TEST")
            (root / "project/issues/ISSUE-TEST.md").write_text(
                "# ISSUE-TEST\n\n**Status:** `REVIEWING`  \n**Starting SHA:** `0000000000000000000000000000000000000000`  \n",
                encoding="utf-8",
            )
            if not commit(root, "wrong starting SHA"):
                errors.append("wrong-starting-SHA fixture could not create candidate")
            else:
                assert_preflight_rejected(
                    errors, "mismatched Starting SHA", root, mock, "issue", "ISSUE-TEST", base, sha(root)
                )

    with tempfile.TemporaryDirectory(prefix="claudex-missing-milestone-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        write_state(root, "MILESTONE_REVIEW", milestone="M1")
        # make_copy() copies the live repository tree, which may already contain
        # a real project/milestones/M1.md once a project reaches its own M1
        # milestone. This fixture must exercise a GENUINELY missing record
        # regardless of the source repo's current state, so remove any copied
        # milestone record before asserting rejection.
        milestone_record = root / "project/milestones/M1.md"
        if milestone_record.exists():
            milestone_record.unlink()
        if not initialize(root) or not commit(root, "missing milestone"):
            errors.append("missing-milestone fixture could not initialize")
        else:
            assert_preflight_rejected(errors, "missing milestone record", root, mock, "milestone-general", "M1", sha(root))

    with tempfile.TemporaryDirectory(prefix="claudex-dirty-tree-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        write_state(root, "ROADMAP_REVIEW")
        if not initialize(root) or not commit(root, "clean plan"):
            errors.append("dirty-worktree fixture could not initialize")
        else:
            head = sha(root)
            (root / "untracked-dirty-file").write_text("dirty\n", encoding="utf-8")
            assert_preflight_rejected(errors, "dirty worktree", root, mock, "plan", head)

    with tempfile.TemporaryDirectory(prefix="claudex-wrong-head-") as temp_dir:
        root = make_copy(temp_dir)
        mock = Path(temp_dir) / "mock-codex"
        create_mock(mock, "PASS")
        write_state(root, "ROADMAP_REVIEW")
        if not initialize(root) or not commit(root, "requested plan head"):
            errors.append("wrong-current-HEAD fixture could not initialize")
        else:
            requested = sha(root)
            (root / "HEAD-MOVED.md").write_text("new commit\n", encoding="utf-8")
            if not commit(root, "move HEAD"):
                errors.append("wrong-current-HEAD fixture could not move HEAD")
            else:
                assert_preflight_rejected(errors, "requested head differs from current HEAD", root, mock, "plan", requested)


def validate_model_floor(errors: list[str], core: Path) -> None:
    """Directly exercise the governed Codex model floor in the launcher.

    A security review must never be pointed at a non-approved model, its default
    must be the account default (None), and a non-security review may be tiered
    down to a specific model.
    """
    spec = importlib.util.spec_from_file_location("claudex_launcher_under_test", core)
    if spec is None or spec.loader is None:
        errors.append("could not load the launcher for model-floor checks")
        return
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # defensive: import must not crash the validator
        errors.append(f"launcher import failed during model-floor checks: {exc}")
        return
    if module.resolve_review_model("milestone-security", None) is not None:
        errors.append("security review default model must be the account default (None)")
    if module.resolve_review_model("plan", "cheaper-model") != "cheaper-model":
        errors.append("non-security review model override was not honored")
    try:
        module.resolve_review_model("milestone-security", "cheaper-model")
    except module.LauncherError as exc:
        if exc.code != 64:
            errors.append(f"security model floor used the wrong exit code: {exc.code}")
    else:
        errors.append("security model floor did not reject a non-approved model")

    # Flag emission: a configured model must appear as a -c model override, and no
    # override must be emitted when the model is the account default (None). This
    # proves the launcher passes the model correctly even though the live Codex
    # CLI is not installed in this environment.
    build = module.build_provider_args
    paths = {"checkout": Path("/co"), "schema_path": Path("/s"), "final_path": Path("/f")}
    with_model = build(Path("codex"), model="some-model-id", **paths)
    if "-c" not in with_model or 'model="some-model-id"' not in with_model:
        errors.append("launcher did not emit the configured Codex model override")
    without_model = build(Path("codex"), model=None, **paths)
    if any(isinstance(arg, str) and arg.startswith('model="') for arg in without_model):
        errors.append("launcher emitted a model override when none was configured")


def validate_launchers(errors: list[str], notices: list[str]) -> None:
    shell = ROOT / "scripts/run-codex-review.sh"
    powershell = ROOT / "scripts/run-codex-review.ps1"
    core = ROOT / "scripts/run_codex_review.py"
    if os.name != "nt" and shell.exists() and not shell.stat().st_mode & stat.S_IXUSR:
        errors.append("scripts/run-codex-review.sh must be executable")
    if shutil.which("sh"):
        result = checked(["sh", "-n", str(shell)], ROOT)
        if result.returncode:
            errors.append(f"POSIX launcher failed syntax check: {result.stderr.strip()}")
    else:
        notices.append("POSIX shell syntax check skipped because sh is unavailable.")
    pwsh = shutil.which("pwsh")
    if pwsh:
        parser = (
            "$path=Join-Path (Get-Location) 'scripts/run-codex-review.ps1'; "
            "$tokens=$null; $errors=$null; "
            "[void][System.Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors); "
            "if($errors.Count){$errors|%{[Console]::Error.WriteLine($_.Message)};exit 1}"
        )
        result = checked([pwsh, "-NoProfile", "-NonInteractive", "-Command", parser], ROOT)
        if result.returncode:
            errors.append(f"PowerShell launcher failed syntax check: {result.stderr.strip()}")
    else:
        notices.append("PowerShell syntax check skipped because pwsh is unavailable; CI runs it on Ubuntu.")
    compiled = checked([sys.executable, "-m", "py_compile", str(core)], ROOT)
    if compiled.returncode:
        errors.append(f"Python launcher failed syntax check: {compiled.stderr.strip()}")
    content = core.read_text(encoding="utf-8").lower()
    for forbidden in ("exec resume", "codex resume", "--dangerously-bypass-approvals-and-sandbox"):
        if forbidden in content:
            errors.append(f"Python launcher contains forbidden token: {forbidden}")
    for required in (
        "--ephemeral", "read-only", "approval_policy", "--output-last-message", "--output-schema",
        "--ignore-user-config", "--ignore-rules", "--test-provider", "codex_bin overrides are not supported", "isolated checkout",
        '"120000", "160000"', '"ls-tree", "-r", "-z"',
        "mode_models", "approved_strong_models", "security_floor_modes", "resolve_review_model",
        "build_provider_args", "security reviews must not be downgraded",
    ):
        if required not in content:
            errors.append(f"Python launcher is missing control: {required}")
    validate_model_floor(errors, core)
    if shutil.which("git") and shutil.which("sh"):
        smoke_plan(errors, "PASS")
        smoke_plan(errors, "CHANGES_REQUIRED")
        smoke_issue(errors)
        smoke_milestones(errors)
        smoke_rejections(errors)
        smoke_target_binding_rejections(errors)
    else:
        notices.append("Mock launcher smoke tests skipped because Git or sh is unavailable.")


def main() -> int:
    errors: list[str] = []
    notices: list[str] = []
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        elif path.stat().st_size == 0 and relative != "project/intake/PROJECT_DESCRIPTION.md":
            errors.append(f"required file is empty: {relative}")
    validate_formats(errors, notices)
    validate_links(errors)
    validate_workflow(errors)
    validate_launchers(errors, notices)
    for notice in notices:
        print(f"NOTICE: {notice}")
    if errors:
        print(f"Repository validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Repository validation passed ({len(REQUIRED_FILES)} required files checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
