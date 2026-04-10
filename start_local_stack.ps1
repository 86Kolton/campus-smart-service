param(
    [switch]$Restart
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Error "Python not found: $python. Create project-root .venv first."
    exit 1
}

function Stop-PortProcesses {
    param([int[]]$Ports)
    foreach ($port in $Ports) {
        $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
        if ($listeners) {
            $pids = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($procId in $pids) {
                try {
                    Stop-Process -Id $procId -Force -ErrorAction Stop
                    Write-Host "[stop] port $port -> PID $procId stopped" -ForegroundColor Yellow
                } catch {
                    Write-Warning "[stop] port $port -> PID $procId failed: $($_.Exception.Message)"
                }
            }
        }
    }
}

if ($Restart) {
    Stop-PortProcesses -Ports @(8000, 5173)
}

$backendLogOut = Join-Path $root "backend\uvicorn.stdout.log"
$backendLogErr = Join-Path $root "backend\uvicorn.stderr.log"
$backendProc = Start-Process `
    -FilePath $python `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory (Join-Path $root "backend") `
    -RedirectStandardOutput $backendLogOut `
    -RedirectStandardError $backendLogErr `
    -PassThru

$frontendProc = Start-Process `
    -FilePath $python `
    -ArgumentList @("-m", "http.server", "5173", "--bind", "127.0.0.1") `
    -WorkingDirectory $root `
    -PassThru

Start-Sleep -Seconds 2

Write-Host "[ok] Backend  PID=$($backendProc.Id)  http://127.0.0.1:8000/healthz" -ForegroundColor Green
Write-Host "[ok] Frontend PID=$($frontendProc.Id) http://127.0.0.1:5173/index.html" -ForegroundColor Green
Write-Host "[tip] Studio: http://127.0.0.1:8000/studio/" -ForegroundColor Cyan
