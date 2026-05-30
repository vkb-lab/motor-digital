$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$PidPath = "memory\command_center_scheduler\pids.json"

if (-not (Test-Path $PidPath)) {
    Write-Host "Nenhum PID do scheduler encontrado."
    exit 0
}

$Data = Get-Content $PidPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($Data.scheduler_pid) {
    Stop-Process -Id ([int]$Data.scheduler_pid) -Force -ErrorAction SilentlyContinue
}

Remove-Item $PidPath -Force -ErrorAction SilentlyContinue

Write-Host "K-Atlas Command Center Scheduler parado."
