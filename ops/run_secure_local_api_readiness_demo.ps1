$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd "C:\Users\oi\Desktop\motor-digital"
if (Test-Path ".\venv\Scripts\python.exe") { $Python = ".\venv\Scripts\python.exe" } elseif (Test-Path ".\.venv\Scripts\python.exe") { $Python = ".\.venv\Scripts\python.exe" } else { throw "Python nao encontrado." }
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
& $Python -m k_atlas.core.secure_local_api_readiness.smoke_test_secure_local_api_readiness
& $Python -m k_atlas.core.secure_local_api_readiness.run_demo
