param()

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$Root'; streamlit run pages\KOS_Safe_Patch_Review_Panel.py --server.port 8519`"";
Start-Sleep -Seconds 2;
Start-Process "http://localhost:8519";
