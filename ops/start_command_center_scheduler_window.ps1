$ErrorActionPreference = "Stop"

$ScriptPath = "C:\Users\oi\Desktop\motor-digital\ops\start_command_center_scheduler.ps1"

Start-Process powershell.exe -WindowStyle Minimized -ArgumentList @(
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $ScriptPath
)

Write-Host "K-Atlas Command Center Scheduler iniciado em janela minimizada."
