# Cross-platform logic lives in the stdlib-only Python launcher. Production
# always invokes the canonical command named "codex"; this wrapper accepts no
# provider override.

$ErrorActionPreference = 'Stop'
$Launcher = Join-Path $PSScriptRoot 'run_codex_review.py'
$Python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Python) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $Python) {
    [Console]::Error.WriteLine('run-codex-review: Python 3 is required.')
    exit 64
}

& $Python.Source $Launcher @args
exit $LASTEXITCODE
