param(
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"

$backendDir = $PSScriptRoot
$projectRoot = Split-Path -Parent $backendDir
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "未找到解释器：$python。请先在项目根目录创建 .venv。"
    exit 1
}

Set-Location $backendDir

$args = @("-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$Port")
if (-not $NoReload) {
    $args += "--reload"
}

Write-Host "[start_backend] python=$python" -ForegroundColor Cyan
Write-Host "[start_backend] http://127.0.0.1:$Port/docs" -ForegroundColor Green
Write-Host "[start_backend] http://127.0.0.1:$Port/studio/" -ForegroundColor Green

& $python @args
