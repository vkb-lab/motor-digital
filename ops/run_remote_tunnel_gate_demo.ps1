$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd "C:\Users\oi\Desktop\motor-digital"
if (Test-Path ".\venv\Scripts\python.exe") { $Python = ".\venv\Scripts\python.exe" } elseif (Test-Path ".\.venv\Scripts\python.exe") { $Python = ".\.venv\Scripts\python.exe" } else { throw "Python nao encontrado." }
$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"
& $Python -m k_atlas.core.remote_tunnel_gate.smoke_test_remote_tunnel_gate
& $Python -m k_atlas.core.remote_tunnel_gate.run_demo
