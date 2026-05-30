$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Startup = [Environment]::GetFolderPath("Startup")
$Launcher = Join-Path $Startup "K-Atlas-Local-Daemon.cmd"

$Content = '@echo off
cd /d C:\Users\oi\Desktop\motor-digital
start "K-Atlas Local Daemon" /min powershell.exe -ExecutionPolicy Bypass -File "C:\Users\oi\Desktop\motor-digital\ops\start_k_atlas_daemon.ps1"
'

Set-Content -Path $Launcher -Value $Content -Encoding ASCII

Write-Host "K-Atlas Local Daemon instalado para iniciar com o Windows."
Write-Host $Launcher
