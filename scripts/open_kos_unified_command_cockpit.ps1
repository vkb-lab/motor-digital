param()

$ErrorActionPreference="Stop";
$Root=Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

python scripts\run_phase72b_unified_command_cockpit_inventory.py | Out-Null;
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; python -m streamlit run pages\KOS_Unified_Command_Cockpit.py --server.port 8522`"";
Start-Sleep -Seconds 3;
Start-Process "http://localhost:8522";
