param()

$ErrorActionPreference="Stop";
$Root=Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; streamlit run pages\KOS_Social_Ops_Control_Center.py --server.port 8520`"";
Start-Sleep -Seconds 2;
Start-Process "http://localhost:8520";
