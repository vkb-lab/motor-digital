$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

powershell -NoExit -ExecutionPolicy Bypass -File ".\ops\start_k_atlas_auto_update_watcher.ps1"