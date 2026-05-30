$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd "C:\Users\oi\Desktop\motor-digital"
powershell -ExecutionPolicy Bypass -File ".\ops\open_operator_home.ps1"
Write-Host "K-Atlas One-Click Launcher executado: Operator Home solicitado."
