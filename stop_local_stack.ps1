$ErrorActionPreference = "Stop"

foreach ($port in @(8000, 5173)) {
    $listeners = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
    if (-not $listeners) {
        Write-Host "[skip] port $port has no listener"
        continue
    }

    $pids = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $pids) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "[ok] port $port -> PID $procId stopped" -ForegroundColor Green
        } catch {
            Write-Warning "[warn] port $port -> PID $procId failed: $($_.Exception.Message)"
        }
    }
}
