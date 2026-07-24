#!/bin/sh

# Cross-platform logic lives in the stdlib-only Python launcher. Production
# always invokes the canonical command named "codex"; this wrapper accepts no
# provider override.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/run_codex_review.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT_DIR/run_codex_review.py" "$@"
fi

printf 'run-codex-review: Python 3 is required.\n' >&2
exit 64
