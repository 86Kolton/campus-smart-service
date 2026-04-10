param(
    [switch]$SkipSmoke
)

$ErrorActionPreference = "Stop"

$backendDir = $PSScriptRoot
$projectRoot = Split-Path -Parent $backendDir
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python interpreter not found: $python. Create project-root .venv first."
    exit 1
}

Set-Location $backendDir

Write-Host "run_tests python=$python" -ForegroundColor Cyan
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if (-not $SkipSmoke) {
    & $python .\scripts\smoke_test.py
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Write-Host "run_tests all checks passed" -ForegroundColor Green
