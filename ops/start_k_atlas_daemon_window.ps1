$ErrorActionPreference = "Stop"

$ScriptPath = "C:\Users\oi\Desktop\motor-digital\ops\start_k_atlas_daemon.ps1"

Start-Process powershell.exe -WindowStyle Minimized -ArgumentList @(
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $ScriptPath
)

Write-Host "K-Atlas Local Daemon iniciado em janela minimizada."
