param(
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"
$backendDir = $PSScriptRoot

$listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($listener) {
    $pids = $listener | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $pids) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[restart_backend] 已停止进程 PID=$procId (port=$Port)" -ForegroundColor Yellow
        } catch {
            Write-Warning "[restart_backend] 停止 PID=$procId 失败：$($_.Exception.Message)"
        }
    }
}

$startScript = Join-Path $backendDir "start_backend.ps1"
if (-not (Test-Path $startScript)) {
    Write-Error "未找到 $startScript"
    exit 1
}

if ($NoReload) {
    & $startScript -Port $Port -NoReload
} else {
    & $startScript -Port $Port
}
