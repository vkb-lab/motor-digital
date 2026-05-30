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

& $Python -m k_atlas.core.autonomy_policy_engine.smoke_test_autonomy_policy_engine
& $Python -m k_atlas.core.safe_task_planner.smoke_test_safe_task_planner
& $Python -m k_atlas.core.supervised_autonomy_queue.smoke_test_supervised_autonomy_queue
& $Python -m k_atlas.core.autonomy_audit_monitor.smoke_test_autonomy_audit_monitor
& $Python -m k_atlas.core.supervised_autonomy_dashboard.smoke_test_supervised_autonomy_dashboard

& $Python -m k_atlas.core.autonomy_policy_engine.run_demo
& $Python -m k_atlas.core.safe_task_planner.run_demo
& $Python -m k_atlas.core.supervised_autonomy_queue.run_demo
& $Python -m k_atlas.core.autonomy_audit_monitor.run_demo
& $Python -m k_atlas.core.supervised_autonomy_dashboard.run_demo
