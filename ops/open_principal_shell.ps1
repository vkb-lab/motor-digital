$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "C:\Users\oi\Desktop\motor-digital\ops\k_shell_cover.ps1"
Write-Host "K-Atlas Principal Shell aberto."
