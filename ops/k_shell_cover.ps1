$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

$Host.UI.RawUI.WindowTitle = "K-Atlas Local OS - Principal Shell"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    $Python = "python"
}

$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

Clear-Host
& $Python -m k_atlas.core.principal_shell_cover.run_demo

Write-Host "Comando fixo para atualizar esta capa:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\ops\k_shell_cover.ps1"
Write-Host ""
