$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    throw "Python virtualenv nao encontrado."
}

$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

Write-Host "Iniciando K-Atlas Secure Local API em localhost..."
Write-Host "URL: http://127.0.0.1:8787/health"
& $Python -m k_atlas.core.secure_local_api_runtime.server --host 127.0.0.1 --port 8787
