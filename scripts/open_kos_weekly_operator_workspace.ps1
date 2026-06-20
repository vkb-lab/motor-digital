param()

$ErrorActionPreference="Stop";
$Root=Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

python scripts\run_phase72a_weekly_operator_workspace.py | Out-Null;
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; python -m streamlit run pages\KOS_Weekly_Operator_Workspace.py --server.port 8521`"";
Start-Sleep -Seconds 3;
Start-Process "http://localhost:8521";
