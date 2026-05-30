$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Startup = [Environment]::GetFolderPath("Startup")
$Launcher = Join-Path $Startup "K-Atlas-Command-Center-Scheduler.cmd"

$Content = '@echo off
cd /d C:\Users\oi\Desktop\motor-digital
start "K-Atlas Command Center Scheduler" /min powershell.exe -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\start_command_center_scheduler.ps1"
'

Set-Content -Path $Launcher -Value $Content -Encoding ASCII

Write-Host "K-Atlas Command Center Scheduler instalado para iniciar com o Windows."
Write-Host $Launcher
