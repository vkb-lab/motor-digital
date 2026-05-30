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

& $Python -m k_atlas.core.local_os_mvp_readiness.smoke_test_local_os_mvp_readiness
& $Python -m k_atlas.core.local_os_release_capsule.smoke_test_local_os_release_capsule
& $Python -m k_atlas.core.local_os_mvp_readiness.run_demo
& $Python -m k_atlas.core.local_os_release_capsule.run_demo
