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

& $Python -m k_atlas.core.secure_local_api_runtime.smoke_test_secure_local_api_runtime
& $Python -m k_atlas.core.local_api_auth_policy.smoke_test_local_api_auth_policy
& $Python -m k_atlas.core.local_api_approval_bridge.smoke_test_local_api_approval_bridge
& $Python -m k_atlas.core.local_api_audit_ledger.smoke_test_local_api_audit_ledger
& $Python -m k_atlas.core.secure_local_api_dashboard.smoke_test_secure_local_api_dashboard
& $Python -m k_atlas.core.secure_local_api_dashboard.run_demo
