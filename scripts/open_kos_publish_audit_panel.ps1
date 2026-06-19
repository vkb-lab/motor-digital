param()

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; streamlit run pages\KOS_Publish_Audit_Panel.py --server.port 8518`"";
Start-Sleep -Seconds 2;
Start-Process "http://localhost:8518";
