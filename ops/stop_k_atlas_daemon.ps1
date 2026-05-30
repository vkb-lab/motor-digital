$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$PidPath = "memory\local_daemon\pids.json"

if (-not (Test-Path $PidPath)) {
    Write-Host "Nenhum PID encontrado."
    exit 0
}

$Data = Get-Content $PidPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($Data.children) {
    $Data.children.PSObject.Properties | ForEach-Object {
        Stop-Process -Id ([int]$_.Value) -Force -ErrorAction SilentlyContinue
    }
}

if ($Data.daemon_pid) {
    Stop-Process -Id ([int]$Data.daemon_pid) -Force -ErrorAction SilentlyContinue
}

Remove-Item $PidPath -Force -ErrorAction SilentlyContinue

Write-Host "K-Atlas Local Daemon parado."
