$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd "C:\Users\oi\Desktop\motor-digital"
if (Test-Path ".\venv\Scripts\python.exe") { $Python = ".\venv\Scripts\python.exe" } elseif (Test-Path ".\.venv\Scripts\python.exe") { $Python = ".\.venv\Scripts\python.exe" } else { throw "Python nao encontrado." }
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
& $Python -m k_atlas.core.lan_cockpit_access.smoke_test_lan_cockpit_access
& $Python -m k_atlas.core.lan_cockpit_access.run_demo
