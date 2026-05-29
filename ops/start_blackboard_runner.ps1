$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    python -m venv venv
    $Python = ".\venv\Scripts\python.exe"
}

$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

Write-Host "K-Atlas Blackboard Runner iniciado."
Write-Host "Aguardando comandos aprovados em memory/blackboard/command_queue.json"
Write-Host "Para parar: Ctrl+C"

& $Python -m k_atlas.core.blackboard.powershell_runner --project-root "C:\Users\oi\Desktop\motor-digital" --interval 10