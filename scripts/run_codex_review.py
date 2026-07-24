#!/usr/bin/env python3
"""Launch one isolated, schema-bound Codex review.

The public shell and PowerShell launchers delegate here. Production execution
always resolves the command named ``codex``; the explicit test-provider option
is for repository validation only and can never create authoritative evidence
or return a production PASS exit status.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
from typing import Any, NoReturn


EXIT_USAGE = 64
EXIT_MALFORMED = 65
EXIT_EXECUTION = 69
EXIT_TEST_ONLY = 78
MAX_FINAL_BYTES = 2 * 1024 * 1024
MAX_JSONL_BYTES = 8 * 1024 * 1024
PROCESS_TIMEOUT_SECONDS = 45 * 60

ROOT = Path(__file__).resolve().parent.parent
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
STATE_RE = re.compile(
    r"\A<!-- claudex-state\r?\n"
    r"stage: ([A-Z][A-Z0-9_]*)\r?\n"
    r"active_issue: ([A-Za-z0-9_-]+|none)\r?\n"
    r"active_milestone: ([A-Za-z0-9_-]+|none)\r?\n"
    r"-->\r?\n"
)

MODE_CONFIG: dict[str, dict[str, Any]] = {
    "plan": {
        "prompt": "prompts/03-codex-plan-review.md",
        "target": "ROADMAP.md",
        "outcomes": ("PASS", "PASS_WITH_NOTES", "CHANGES_REQUIRED", "BLOCKED", "USER_DECISION_REQUIRED"),
    },
    "issue": {
        "prompt": "prompts/05-codex-issue-review.md",
        "outcomes": ("PASS", "PASS_WITH_NOTES", "CHANGES_REQUIRED", "BLOCKED", "USER_DECISION_REQUIRED"),
    },
    "milestone-general": {
        "prompt": "prompts/07-milestone-general-review.md",
        "outcomes": ("PASS", "PASS_WITH_NOTES", "CHANGES_REQUIRED", "BLOCKED"),
    },
    "milestone-security": {
        "prompt": "prompts/08-milestone-security-review.md",
        "outcomes": ("PASS", "PASS_WITH_NOTES", "REMEDIATION_REQUIRED", "BLOCKED", "INCONCLUSIVE"),
    },
}

# --- Governed per-mode Codex model selection --------------------------------
# None means "do not override the Codex CLI's configured default model": the
# strong default, and the behaviour before model selection existed. A human may
# pin a specific provider/account model id here to tier a NON-security review
# down to a cheaper model. This is a governed decision recorded in
# docs/model-assignment.md, not an ad-hoc runtime flag, so it lives in committed
# source rather than an environment override.
#
# To tier a non-security review down, replace None with your account's model id,
# for example:
#     "plan": "o4-mini",
#     "issue": "o4-mini",
# Leave "milestone-security" as None (or a vetted id in APPROVED_STRONG_MODELS);
# the floor below rejects any weak model for it.
MODE_MODELS: dict[str, str | None] = {
    "plan": None,
    "issue": None,
    "milestone-general": None,
    "milestone-security": None,
}

# Model ids a human has vetted as strong enough to run a floored gate review.
# Empty by default: with no vetted ids, a floored mode may use only None, i.e.
# the account's configured default model. Adding an id here is a governed change.
APPROVED_STRONG_MODELS: frozenset[str] = frozenset()

# Modes whose Codex model must never be silently weakened. A floored mode may use
# only None (the account default) or an id listed in APPROVED_STRONG_MODELS, so a
# security review can never be downgraded to a cheap model by configuration.
SECURITY_FLOOR_MODES: frozenset[str] = frozenset({"milestone-security"})

MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class LauncherError(Exception):
    """A deliberate fail-closed launcher error with a stable exit status."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def fail(code: int, message: str) -> NoReturn:
    raise LauncherError(code, message)


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            env=env,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        fail(EXIT_EXECUTION, f"could not execute {args[0]!r}: {exc}")


def git(args: list[str], *, cwd: Path = ROOT, check_code: int = EXIT_USAGE) -> str:
    clean_env = {
        "PATH": os.environ.get("PATH", os.defpath),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GCM_INTERACTIVE": "Never",
        "LC_ALL": "C",
    }
    result = run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=cwd, env=clean_env)
    if result.returncode:
        detail = result.stderr.strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        fail(check_code, f"Git command failed ({args[0]}){suffix}")
    return result.stdout


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--test-provider", metavar="PATH")
    parser.add_argument("mode", nargs="?")
    parser.add_argument("values", nargs="*")
    parser.add_argument("-h", "--help", action="store_true")
    try:
        parsed = parser.parse_args(argv)
    except SystemExit:
        fail(EXIT_USAGE, "invalid arguments")
    if parsed.help or parsed.mode not in MODE_CONFIG:
        fail(
            EXIT_USAGE,
            "usage: run-codex-review plan <HEAD-SHA> | issue <ISSUE-ID> <BASE-SHA> <HEAD-SHA> | "
            "milestone-general <MILESTONE-ID> <SHA> | milestone-security <MILESTONE-ID> <SHA>",
        )
    expected = {"plan": 1, "issue": 3, "milestone-general": 2, "milestone-security": 2}[parsed.mode]
    if len(parsed.values) != expected:
        fail(EXIT_USAGE, f"wrong number of arguments for {parsed.mode}")
    return parsed


def normalize_sha(value: str, label: str) -> str:
    if not SHA_RE.fullmatch(value):
        fail(EXIT_USAGE, f"{label} must be a full 40-character hexadecimal commit ID")
    return value.lower()


def normalize_id(value: str, label: str) -> str:
    if not ID_RE.fullmatch(value):
        fail(EXIT_USAGE, f"{label} must contain only letters, numbers, underscore, or hyphen")
    return value


def git_blob(commit: str, path: str) -> str:
    result = run(
        ["git", "-c", "core.hooksPath=/dev/null", "show", f"{commit}:{path}"],
        cwd=ROOT,
        env={
            "PATH": os.environ.get("PATH", os.defpath),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "LC_ALL": "C",
        },
    )
    if result.returncode:
        fail(EXIT_USAGE, f"required committed record {path} is missing at {commit}")
    return result.stdout


def validate_repository_identity() -> Path:
    if shutil.which("git") is None:
        fail(EXIT_USAGE, "Git is required")
    top = Path(git(["rev-parse", "--show-toplevel"]).strip()).resolve()
    if os.path.normcase(str(top)) != os.path.normcase(str(ROOT.resolve())):
        fail(EXIT_USAGE, "launcher must run from its own repository root")
    common_raw = git(["rev-parse", "--git-common-dir"]).strip()
    common = Path(common_raw)
    if not common.is_absolute():
        common = ROOT / common
    common = common.resolve(strict=True)
    if not common.is_dir():
        fail(EXIT_USAGE, "Git common directory is unavailable")
    return common


def validate_clean_target(head_sha: str, base_sha: str) -> None:
    git(["cat-file", "-e", f"{head_sha}^{{commit}}"])
    current = git(["rev-parse", "HEAD"]).strip().lower()
    if current != head_sha:
        fail(EXIT_USAGE, f"current HEAD {current} does not equal target {head_sha}")
    if git(["status", "--porcelain=v1", "-z", "--untracked-files=all"]):
        fail(EXIT_USAGE, "worktree must be clean before review")
    if base_sha:
        git(["cat-file", "-e", f"{base_sha}^{{commit}}"])
        result = run(
            ["git", "-c", "core.hooksPath=/dev/null", "merge-base", "--is-ancestor", base_sha, head_sha],
            cwd=ROOT,
            env={
                "PATH": os.environ.get("PATH", os.defpath),
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "LC_ALL": "C",
            },
        )
        if result.returncode:
            fail(EXIT_USAGE, "base commit is not an ancestor of target commit")


def parse_state(head_sha: str) -> dict[str, str]:
    text = git_blob(head_sha, "project/status/CURRENT.md")
    if text.count("<!-- claudex-state") != 1:
        fail(EXIT_USAGE, "project/status/CURRENT.md must contain exactly one claudex-state block")
    match = STATE_RE.match(text)
    if not match:
        fail(EXIT_USAGE, "project/status/CURRENT.md must begin with the exact claudex-state comment block")
    return {
        "stage": match.group(1),
        "active_issue": match.group(2),
        "active_milestone": match.group(3),
    }


def validate_target_binding(mode: str, target_id: str, base_sha: str, head_sha: str) -> str:
    state = parse_state(head_sha)
    if mode == "plan":
        if state["stage"] != "ROADMAP_REVIEW":
            fail(EXIT_USAGE, "plan review requires committed stage ROADMAP_REVIEW")
        git_blob(head_sha, "ROADMAP.md")
        return "ROADMAP.md"
    if mode == "issue":
        if state["stage"] not in {"ISSUE_REVIEW", "ISSUE_REPAIR"}:
            fail(EXIT_USAGE, "issue review requires committed stage ISSUE_REVIEW or ISSUE_REPAIR")
        if state["active_issue"] != target_id:
            fail(EXIT_USAGE, "active_issue does not match the requested issue ID")
        if base_sha == head_sha:
            fail(EXIT_USAGE, "issue review requires distinct base and head commits")
        target = f"project/issues/{target_id}.md"
        issue = git_blob(head_sha, target)
        if not re.search(r"(?m)^\*\*Status:\*\* `(REVIEWING|REPAIRING)`[ \t]*$", issue):
            fail(EXIT_USAGE, "committed issue status must be REVIEWING or REPAIRING")
        starting = re.compile(rf"(?m)^\*\*Starting SHA:\*\* `{re.escape(base_sha)}`[ \t]*$")
        if not starting.search(issue):
            fail(EXIT_USAGE, "committed issue Starting SHA does not match the requested base")
        return target
    if state["stage"] != "MILESTONE_REVIEW":
        fail(EXIT_USAGE, f"{mode} requires committed stage MILESTONE_REVIEW")
    if state["active_milestone"] != target_id:
        fail(EXIT_USAGE, "active_milestone does not match the requested milestone ID")
    target = f"project/milestones/{target_id}.md"
    milestone = git_blob(head_sha, target)
    if not re.search(r"(?m)^\*\*Status:\*\* `REVIEWING`[ \t]*$", milestone):
        fail(EXIT_USAGE, "committed milestone status must be REVIEWING")
    return target


def reject_unsafe_tree(commit: str) -> None:
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "ls-tree", "-r", "-z", commit],
        cwd=ROOT,
        env={
            "PATH": os.environ.get("PATH", os.defpath),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "LC_ALL": "C",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        fail(EXIT_USAGE, f"could not inspect tree at {commit}")
    for raw_entry in result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, object_type, _object_id = metadata.decode("ascii").split(" ", 2)
            path = raw_path.decode("utf-8", "strict")
        except (ValueError, UnicodeError):
            fail(EXIT_USAGE, f"tree at {commit} contains an unparseable path")
        parts = path.replace("\\", "/").split("/")
        if not path or path.startswith(("/", "\\")) or any(part in {"", ".", ".."} for part in parts):
            fail(EXIT_USAGE, f"tree at {commit} contains an unsafe path")
        if mode in {"120000", "160000"} or object_type == "commit":
            kind = "symlink" if mode == "120000" else "gitlink"
            fail(EXIT_USAGE, f"tree at {commit} contains unsupported {kind}: {path}")


def isolated_git_env() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", os.defpath),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GCM_INTERACTIVE": "Never",
        "LC_ALL": "C",
    }


def create_isolated_checkout(parent: Path, head_sha: str, base_sha: str) -> Path:
    checkout = parent / "checkout"
    checkout.mkdir(mode=0o700)
    env = isolated_git_env()
    commands = [
        ["git", "init", "-q", str(checkout)],
        ["git", "-C", str(checkout), "config", "core.hooksPath", os.devnull],
        ["git", "-C", str(checkout), "config", "core.autocrlf", "false"],
        ["git", "-C", str(checkout), "config", "core.attributesFile", os.devnull],
        [
            "git", "-C", str(checkout), "-c", "protocol.file.allow=always", "fetch", "-q",
            "--no-tags", "--no-recurse-submodules", "--depth=1", str(ROOT),
            f"{head_sha}:refs/claudex/head",
        ],
    ]
    if base_sha:
        commands.append(
            [
                "git", "-C", str(checkout), "-c", "protocol.file.allow=always", "fetch", "-q",
                "--no-tags", "--no-recurse-submodules", "--depth=1", str(ROOT),
                f"{base_sha}:refs/claudex/base",
            ]
        )
    commands.append(["git", "-C", str(checkout), "checkout", "-q", "--detach", head_sha])
    for command in commands:
        result = run(command, env=env)
        if result.returncode:
            fail(EXIT_EXECUTION, "could not construct isolated review checkout")

    expected = {head_sha} | ({base_sha} if base_sha else set())
    objects = run(
        ["git", "-C", str(checkout), "cat-file", "--batch-all-objects", "--batch-check=%(objecttype) %(objectname)"],
        env=env,
    )
    if objects.returncode:
        fail(EXIT_EXECUTION, "could not verify isolated review objects")
    commits = {line.split()[1] for line in objects.stdout.splitlines() if line.startswith("commit ")}
    if commits != expected:
        fail(EXIT_EXECUTION, "isolated checkout contains commits outside the requested review pair")

    git_dir = checkout / ".git"
    for trace in (git_dir / "FETCH_HEAD", git_dir / "logs"):
        if trace.is_dir():
            shutil.rmtree(trace)
        elif trace.exists():
            trace.unlink()
    return checkout


def review_schema(mode: str, outcomes: tuple[str, ...]) -> dict[str, Any]:
    finding_required = [
        "id", "classification", "severity", "confidence", "blocking", "title",
        "locations", "evidence", "remediation", "verification",
    ]
    finding_properties: dict[str, Any] = {
        "id": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$"},
        "classification": {"enum": ["BLOCKER", "REQUIRED", "ADVISORY", "QUESTION"]},
        "severity": {"enum": ["critical", "high", "medium", "low", "info"]},
        "confidence": {"enum": ["high", "medium", "low"]},
        "blocking": {"type": "boolean"},
        "title": {"type": "string", "minLength": 1, "maxLength": 500},
        "locations": {
            "type": "array", "minItems": 1, "maxItems": 50,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["path", "line"],
                "properties": {
                    "path": {"type": "string", "minLength": 1, "maxLength": 1000},
                    "line": {"type": "integer", "minimum": 0},
                },
            },
        },
        "evidence": {
            "type": "array", "minItems": 1, "maxItems": 50,
            "items": {"type": "string", "minLength": 1, "maxLength": 10000},
        },
        "remediation": {"type": "string", "minLength": 1, "maxLength": 10000},
        "verification": {"type": "string", "minLength": 1, "maxLength": 10000},
    }
    if mode == "milestone-security":
        finding_required.extend(
            ["fingerprint", "category", "attack_preconditions", "impact", "exploitability", "disposition"]
        )
        finding_properties.update(
            {
                "fingerprint": {"type": "string", "minLength": 1, "maxLength": 500},
                "category": {"type": "string", "minLength": 1, "maxLength": 500},
                "attack_preconditions": {"type": "string", "minLength": 1, "maxLength": 10000},
                "impact": {"type": "string", "minLength": 1, "maxLength": 10000},
                "exploitability": {"type": "string", "minLength": 1, "maxLength": 10000},
                "disposition": {"enum": ["open", "closed", "risk-candidate"]},
            }
        )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version", "mode", "target_id", "base_sha", "reviewed_sha", "outcome",
            "summary", "findings", "evidence", "limitations",
        ],
        "properties": {
            "schema_version": {"const": "1.0"},
            "mode": {"const": mode},
            "target_id": {"type": "string", "maxLength": 64},
            "base_sha": {"type": "string", "maxLength": 40},
            "reviewed_sha": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
            "outcome": {"enum": list(outcomes)},
            "summary": {"type": "string", "minLength": 1, "maxLength": 20000},
            "findings": {
                "type": "array", "maxItems": 200,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": finding_required,
                    "properties": finding_properties,
                },
            },
            "evidence": {
                "type": "array", "minItems": 1, "maxItems": 200,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["source", "reference", "detail"],
                    "properties": {
                        "source": {"enum": ["file", "diff", "check", "command", "limitation"]},
                        "reference": {"type": "string", "minLength": 1, "maxLength": 2000},
                        "detail": {"type": "string", "minLength": 1, "maxLength": 10000},
                    },
                },
            },
            "limitations": {
                "type": "array", "maxItems": 100,
                "items": {"type": "string", "minLength": 1, "maxLength": 10000},
            },
        },
    }


def provider_compatible_schema(value: Any) -> Any:
    """Reduce the local schema to the conservative Structured Outputs subset."""
    if isinstance(value, list):
        return [provider_compatible_schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    allowed = {"type", "properties", "required", "additionalProperties", "items", "enum"}
    output: dict[str, Any] = {}
    for key, item in value.items():
        if key == "const":
            output["enum"] = [item]
        elif key == "properties" and isinstance(item, dict):
            # ``properties`` is a MAP of property-name -> subschema, not a schema
            # object. Recurse into each value while preserving the property names;
            # do not pass the names through the keyword filter (that would drop
            # every property and emit an unsatisfiable ``"properties": {}``).
            output["properties"] = {
                name: provider_compatible_schema(subschema)
                for name, subschema in item.items()
            }
        elif key in allowed:
            output[key] = provider_compatible_schema(item)
    return output


def type_is(value: Any, expected: type) -> bool:
    return isinstance(value, expected) and (expected is not int or not isinstance(value, bool))


def validate_shape(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    if "const" in schema and value != schema["const"]:
        fail(EXIT_MALFORMED, f"final report {path} does not match its required binding")
    if "enum" in schema and value not in schema["enum"]:
        fail(EXIT_MALFORMED, f"final report {path} has an unsupported value")
    expected = schema.get("type")
    if expected == "object":
        if not isinstance(value, dict):
            fail(EXIT_MALFORMED, f"final report {path} must be an object")
        required = schema.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            fail(EXIT_MALFORMED, f"final report {path} is missing {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                fail(EXIT_MALFORMED, f"final report {path} has unknown field {extra[0]}")
        for key, child in properties.items():
            if key in value:
                validate_shape(value[key], child, f"{path}.{key}")
    elif expected == "array":
        if not isinstance(value, list):
            fail(EXIT_MALFORMED, f"final report {path} must be an array")
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", sys.maxsize):
            fail(EXIT_MALFORMED, f"final report {path} has an invalid item count")
        for index, child in enumerate(value):
            validate_shape(child, schema["items"], f"{path}[{index}]")
    elif expected == "string":
        if not isinstance(value, str):
            fail(EXIT_MALFORMED, f"final report {path} must be a string")
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", sys.maxsize):
            fail(EXIT_MALFORMED, f"final report {path} has an invalid length")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            fail(EXIT_MALFORMED, f"final report {path} has an invalid format")
    elif expected == "integer":
        if not type_is(value, int) or value < schema.get("minimum", -sys.maxsize):
            fail(EXIT_MALFORMED, f"final report {path} must be a valid integer")
    elif expected == "boolean" and not isinstance(value, bool):
        fail(EXIT_MALFORMED, f"final report {path} must be a boolean")


def validate_semantics(
    report: dict[str, Any], *, mode: str, target_id: str, base_sha: str, head_sha: str
) -> None:
    if report["mode"] != mode or report["target_id"] != target_id:
        fail(EXIT_MALFORMED, "final report mode or target ID does not match the request")
    if report["base_sha"] != base_sha or report["reviewed_sha"] != head_sha:
        fail(EXIT_MALFORMED, "final report commit identity does not match the request")
    findings = report["findings"]
    limitations = report["limitations"]
    ids: set[str] = set()
    for finding in findings:
        if finding["id"] in ids:
            fail(EXIT_MALFORMED, "final report contains duplicate finding IDs")
        ids.add(finding["id"])
        if finding["severity"] in {"critical", "high"} and not finding["blocking"]:
            fail(EXIT_MALFORMED, "critical and high findings must be blocking")
        if finding["classification"] in {"BLOCKER", "REQUIRED"} and not finding["blocking"]:
            fail(EXIT_MALFORMED, "BLOCKER and REQUIRED findings must be blocking")
        for location in finding["locations"]:
            path = location["path"].replace("\\", "/")
            if path.startswith("/") or ".." in path.split("/"):
                fail(EXIT_MALFORMED, "finding location must be repository-relative")
    blocking = [finding for finding in findings if finding["blocking"]]
    outcome = report["outcome"]
    if outcome == "PASS" and (findings or limitations):
        fail(EXIT_MALFORMED, "PASS cannot contain findings or limitations")
    if outcome == "PASS_WITH_NOTES" and (blocking or not (findings or limitations)):
        fail(EXIT_MALFORMED, "PASS_WITH_NOTES requires notes but cannot contain blocking findings")
    if outcome in {"CHANGES_REQUIRED", "REMEDIATION_REQUIRED"} and not blocking:
        fail(EXIT_MALFORMED, f"{outcome} requires at least one blocking finding")
    if outcome in {"BLOCKED", "INCONCLUSIVE"} and not limitations:
        fail(EXIT_MALFORMED, f"{outcome} requires a concrete limitation")
    if outcome == "USER_DECISION_REQUIRED" and not (
        limitations or any(item["classification"] == "QUESTION" for item in findings)
    ):
        fail(EXIT_MALFORMED, "USER_DECISION_REQUIRED requires a question or limitation")
    if blocking and outcome in {"PASS", "PASS_WITH_NOTES"}:
        fail(EXIT_MALFORMED, "a passing outcome cannot contain blocking findings")


def sanitized_environment(executable: Path, temp_root: Path, *, test_only: bool) -> dict[str, str]:
    original = os.environ
    path_entries = [str(executable.parent), str(Path(sys.executable).resolve().parent)]
    for candidate in ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin", "/usr/sbin", "/sbin"):
        if Path(candidate).is_dir():
            path_entries.append(candidate)
    path_value = os.pathsep.join(dict.fromkeys(path_entries))
    env: dict[str, str] = {
        "PATH": path_value,
        "TMPDIR": str(temp_root),
        "TEMP": str(temp_root),
        "TMP": str(temp_root),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GCM_INTERACTIVE": "Never",
        "NO_COLOR": "1",
        "CLAUDEX_REVIEW": "test" if test_only else "authoritative",
    }
    for key in (
        "HOME", "USERPROFILE", "CODEX_HOME", "XDG_CONFIG_HOME", "APPDATA", "LOCALAPPDATA",
        "SYSTEMROOT", "COMSPEC", "PATHEXT", "LANG", "LC_ALL", "LC_CTYPE", "TZ",
        "SSL_CERT_FILE", "SSL_CERT_DIR",
    ):
        if original.get(key):
            env[key] = original[key]
    return env


def resolve_provider(test_provider: str | None) -> tuple[Path, bool]:
    if test_provider:
        candidate = Path(test_provider).expanduser().resolve(strict=True)
        if not candidate.is_file() or (os.name != "nt" and not os.access(candidate, os.X_OK)):
            fail(EXIT_USAGE, "test provider must be an executable file")
        return candidate, True
    if os.environ.get("CODEX_BIN"):
        fail(EXIT_USAGE, "CODEX_BIN overrides are not supported; production always invokes codex")
    resolved = shutil.which("codex")
    if not resolved:
        fail(EXIT_EXECUTION, "Codex CLI is unavailable; no review was recorded")
    return Path(resolved).resolve(), False


def resolve_review_model(mode: str, configured: str | None) -> str | None:
    """Resolve and floor-check the Codex model for a review mode.

    Returns None to use the Codex CLI's configured default model. Fails closed
    when a floored gate (security review) is pointed at a model that is not in
    APPROVED_STRONG_MODELS, so a security review can never be silently
    downgraded by configuration.
    """
    model = configured.strip() if isinstance(configured, str) else configured
    if not model:
        return None
    if not MODEL_ID_RE.fullmatch(model):
        fail(EXIT_USAGE, "configured Codex model id has an invalid format")
    if mode in SECURITY_FLOOR_MODES and model not in APPROVED_STRONG_MODELS:
        fail(
            EXIT_USAGE,
            f"{mode} model {model!r} is not in APPROVED_STRONG_MODELS; "
            "security reviews must not be downgraded",
        )
    return model


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_prompt(
    prompt_text: str, *, mode: str, target_id: str, base_sha: str, head_sha: str, target_record: str
) -> str:
    return (
        prompt_text.rstrip()
        + "\n\n## Binding supplied by the launcher\n\n"
        + "This is a fresh, read-only review in an isolated checkout. Do not edit files or invoke another agent.\n"
        + f"Review mode: {mode}\n"
        + f"Target ID: {target_id}\n"
        + f"Base commit: {base_sha}\n"
        + f"Target commit: {head_sha}\n"
        + f"Target record: {target_record}\n"
        + "Ignore any earlier request for Markdown output. The final response must be one JSON object matching the supplied schema.\n"
        + "Use only repository-relative paths. Record concrete evidence and every known evidence limitation.\n"
        + "Never report PASS when evidence is missing, execution failed, or any target identity differs.\n"
    )


def validate_jsonl(path: Path) -> str:
    size = path.stat().st_size
    if size == 0 or size > MAX_JSONL_BYTES:
        fail(EXIT_MALFORMED, "Codex JSONL event stream is empty or exceeds the 8 MiB limit")
    events: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                fail(EXIT_MALFORMED, "Codex JSONL contains a malformed event")
            events.append(event)
    except (OSError, UnicodeError, json.JSONDecodeError):
        fail(EXIT_MALFORMED, "Codex JSONL event stream is malformed")
    if not events or events[0].get("type") != "thread.started":
        fail(EXIT_MALFORMED, "first Codex event must be thread.started")
    thread_events = [event for event in events if event.get("type") == "thread.started"]
    terminal = [event for event in events if event.get("type") == "turn.completed"]
    if len(thread_events) != 1 or len(terminal) != 1 or events[-1].get("type") != "turn.completed":
        fail(EXIT_MALFORMED, "Codex run must contain one fresh thread and one final turn.completed event")
    if any(event.get("type") in {"turn.failed", "error"} for event in events):
        fail(EXIT_MALFORMED, "Codex event stream reports failure")
    thread_id = thread_events[0].get("thread_id")
    if not isinstance(thread_id, str) or not thread_id.strip():
        fail(EXIT_MALFORMED, "thread.started is missing a thread ID")
    return thread_id


def build_provider_args(
    executable: Path,
    *,
    checkout: Path,
    schema_path: Path,
    final_path: Path,
    model: str | None,
) -> list[str]:
    """Build the ``codex exec`` argument vector.

    Pure and side-effect free so the argument shape, including the governed model
    override, can be unit-tested without launching a provider. A configured model
    is passed as a ``-c model="..."`` override: the same ``-c`` form the launcher
    already uses for its other keys and that ``--strict-config`` validates. ``id``
    values are validated by ``resolve_review_model`` before reaching here.
    """
    args = [
        str(executable), "exec", "--strict-config", "--cd", str(checkout), "--sandbox", "read-only",
        "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
        "-c", "features.apps=false", "-c", "features.hooks=false", "-c", "features.memories=false",
        "-c", "features.multi_agent=false", "-c", "features.skill_mcp_dependency_install=false",
    ]
    if model:
        args += ["-c", f'model="{model}"']
    args += [
        "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json", "--output-schema", str(schema_path),
        "--output-last-message", str(final_path), "-",
    ]
    return args


def run_provider(
    executable: Path,
    *,
    test_only: bool,
    checkout: Path,
    prompt: str,
    schema_path: Path,
    final_path: Path,
    jsonl_path: Path,
    stderr_path: Path,
    environment: dict[str, str],
    model: str | None,
) -> str:
    args = build_provider_args(
        executable, checkout=checkout, schema_path=schema_path, final_path=final_path, model=model
    )
    creationflags = 0
    if os.name == "nt" and hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    with jsonl_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
        try:
            process = subprocess.Popen(
                args,
                cwd=checkout,
                env=environment,
                stdin=subprocess.PIPE,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=(os.name != "nt"),
                creationflags=creationflags,
            )
            process.communicate(prompt.encode("utf-8"), timeout=PROCESS_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
            fail(EXIT_EXECUTION, "Codex review exceeded the 45-minute wall-clock limit")
        except OSError as exc:
            fail(EXIT_EXECUTION, f"could not launch {'test provider' if test_only else 'codex'}: {exc}")
    if process.returncode != 0:
        detail = ""
        try:
            tail = stderr_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()
            if tail:
                detail = f" (provider stderr: {tail[-1][:200]})"
        except OSError:
            pass
        fail(EXIT_EXECUTION, f"Codex execution or authentication failed; no review was recorded{detail}")
    return validate_jsonl(jsonl_path)


def safe_report_path(common: Path, relative_parts: list[str]) -> Path:
    current = common
    for component in relative_parts[:-1]:
        if not ID_RE.fullmatch(component) and component not in {
            "claudex", "reviews", "test-reviews", "plans", "issues", "milestones"
        }:
            fail(EXIT_USAGE, "unsafe report path component")
        next_path = current / component
        try:
            metadata = next_path.lstat()
        except FileNotFoundError:
            os.mkdir(next_path, 0o700)
            metadata = next_path.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            fail(EXIT_USAGE, "report staging path contains a symlink or non-directory")
        current = next_path
    destination = current / relative_parts[-1]
    try:
        destination.lstat()
    except FileNotFoundError:
        return destination
    fail(EXIT_USAGE, "refusing to overwrite an existing staged review report")


def write_exclusive_json(path: Path, value: dict[str, Any]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n", closefd=True) as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def report_locations(mode: str, target_id: str, head_sha: str) -> tuple[list[str], str]:
    short = head_sha[:12]
    if mode == "plan":
        filename = f"ROADMAP-{short}-codex.json"
        folder = "plans"
    elif mode == "issue":
        filename = f"{target_id}-{short}-codex.json"
        folder = "issues"
    elif mode == "milestone-general":
        filename = f"{target_id}-{short}-codex-general.json"
        folder = "milestones"
    else:
        filename = f"{target_id}-{short}-codex-security.json"
        folder = "milestones"
    return [folder, filename], f"project/reviews/{folder}/{filename}"


def outcome_exit(outcome: str) -> int:
    return {
        "PASS": 0,
        "PASS_WITH_NOTES": 10,
        "CHANGES_REQUIRED": 20,
        "REMEDIATION_REQUIRED": 20,
        "BLOCKED": 30,
        "INCONCLUSIVE": 30,
        "USER_DECISION_REQUIRED": 40,
    }[outcome]


def main(argv: list[str]) -> int:
    parsed = parse_args(argv)
    mode: str = parsed.mode
    values: list[str] = parsed.values
    target_id = ""
    base_sha = ""
    if mode == "plan":
        head_sha = normalize_sha(values[0], "target SHA")
    elif mode == "issue":
        target_id = normalize_id(values[0], "issue ID")
        base_sha = normalize_sha(values[1], "base SHA")
        head_sha = normalize_sha(values[2], "target SHA")
    else:
        target_id = normalize_id(values[0], "milestone ID")
        head_sha = normalize_sha(values[1], "target SHA")

    common = validate_repository_identity()
    validate_clean_target(head_sha, base_sha)
    target_record = validate_target_binding(mode, target_id, base_sha, head_sha)
    reject_unsafe_tree(head_sha)
    if base_sha:
        reject_unsafe_tree(base_sha)

    executable, test_only = resolve_provider(parsed.test_provider)
    review_model = resolve_review_model(mode, MODE_MODELS.get(mode))
    config = MODE_CONFIG[mode]
    prompt_path = ROOT / config["prompt"]
    if not prompt_path.is_file() or prompt_path.is_symlink():
        fail(EXIT_USAGE, f"required prompt {config['prompt']} is missing or unsafe")
    prompt_text = git_blob(head_sha, config["prompt"])
    prompt = build_prompt(
        prompt_text,
        mode=mode,
        target_id=target_id,
        base_sha=base_sha,
        head_sha=head_sha,
        target_record=target_record,
    )
    schema = review_schema(mode, config["outcomes"])

    with tempfile.TemporaryDirectory(prefix="claudex-codex-review-") as temporary:
        temp_root = Path(temporary)
        checkout = create_isolated_checkout(temp_root, head_sha, base_sha)
        schema_path = temp_root / "review.schema.json"
        final_path = temp_root / "final.json"
        jsonl_path = temp_root / "events.jsonl"
        stderr_path = temp_root / "stderr.log"
        schema_path.write_text(json.dumps(provider_compatible_schema(schema), sort_keys=True), encoding="utf-8")
        environment = sanitized_environment(executable, temp_root, test_only=test_only)
        version_result = run([str(executable), "--version"], env=environment, timeout=10)
        version = version_result.stdout.strip().splitlines()[0][:200] if version_result.returncode == 0 and version_result.stdout.strip() else "unavailable"
        thread_id = run_provider(
            executable,
            test_only=test_only,
            checkout=checkout,
            prompt=prompt,
            schema_path=schema_path,
            final_path=final_path,
            jsonl_path=jsonl_path,
            stderr_path=stderr_path,
            environment=environment,
            model=review_model,
        )
        try:
            if final_path.stat().st_size == 0 or final_path.stat().st_size > MAX_FINAL_BYTES:
                fail(EXIT_MALFORMED, "Codex final report is empty or exceeds the 2 MiB limit")
            report = json.loads(final_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            fail(EXIT_MALFORMED, "Codex final report is not valid JSON")
        validate_shape(report, schema)
        validate_semantics(report, mode=mode, target_id=target_id, base_sha=base_sha, head_sha=head_sha)

    if git(["rev-parse", "HEAD"]).strip().lower() != head_sha:
        fail(EXIT_MALFORMED, "HEAD changed during review")
    if git(["status", "--porcelain=v1", "-z", "--untracked-files=all"]):
        fail(EXIT_MALFORMED, "candidate worktree changed during the read-only review")

    suffix, intended_record = report_locations(mode, target_id, head_sha)
    root_folder = "test-reviews" if test_only else "reviews"
    staged = safe_report_path(common, ["claudex", root_folder, *suffix])
    envelope = {
        "report_schema": "claudex-review-envelope/1.0",
        "authoritative": not test_only,
        "test_only": test_only,
        "metadata": {
            "provider": "test-double" if test_only else "codex",
            "executable": "test-provider" if test_only else "codex",
            "executable_sha256": sha256_file(executable),
            "cli_version": version,
            "model": review_model if review_model is not None else "codex-cli-default",
            "thread_id": thread_id,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "isolated_checkout": True,
            "event_stream_captured": True,
        },
        "review": report,
    }
    write_exclusive_json(staged, envelope)

    label = "TEST-ONLY, NON-AUTHORITATIVE" if test_only else "AUTHORITATIVE"
    print(f"Review staged under Git metadata: claudex/{root_folder}/{'/'.join(suffix)}")
    print(f"Intended committed record: {intended_record}")
    print(f"Evidence class: {label}")
    print(f"Codex model: {review_model if review_model is not None else 'codex-cli-default'}")
    print(f"Outcome: {report['outcome']}")
    if test_only:
        print("Test-provider results can never satisfy a workflow review gate.")
        return EXIT_TEST_ONLY
    return outcome_exit(report["outcome"])


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except LauncherError as error:
        print(f"run-codex-review: {error}", file=sys.stderr)
        raise SystemExit(error.code)
