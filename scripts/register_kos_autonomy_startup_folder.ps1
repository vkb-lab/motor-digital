$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot

$Required="YES_REGISTER_KOS_STARTUP_LOCAL_ONLY"
$EntryName="KOS-Autonomy-Scheduler-Local.cmd"
$StartupFolder=[Environment]::GetFolderPath("Startup")
$EntryPath=Join-Path $StartupFolder $EntryName

Write-Host "[KOS] Registro via Startup Folder do usuario."
Write-Host "[KOS] Nao requer admin."
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."
Write-Host "[KOS] Startup folder:" $StartupFolder
Write-Host "[KOS] Entry:" $EntryPath

$Confirm=(Read-Host "Para registrar, digite exatamente YES_REGISTER_KOS_STARTUP_LOCAL_ONLY").Trim()

if($Confirm -ne $Required){
  Write-Host "[KOS] Confirmacao incorreta. Nenhum startup foi registrado."
  exit 0
}

New-Item -ItemType Directory -Force $StartupFolder | Out-Null
New-Item -ItemType Directory -Force "logs\kaizen\startup","local_runtime\kaizen" | Out-Null

$SchedulerScript=(Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path
$LogPath=(Resolve-Path "logs\kaizen\startup").Path + "\startup_loop.log"

$Cmd = @"
@echo off
cd /d "$ProjectRoot"
set PYTHONPATH=$ProjectRoot
set KOS_SCHEDULER_INTERVAL_SECONDS=900
set KOS_SCHEDULER_MAX_CYCLES=0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$SchedulerScript" >> "$LogPath" 2>&1
"@

[System.IO.File]::WriteAllText($EntryPath, $Cmd, [System.Text.UTF8Encoding]::new($false))

$Status=[ordered]@{
  status="STARTUP_FOLDER_ENTRY_REGISTERED"
  entry_path=$EntryPath
  startup_folder=$StartupFolder
  requires_admin=$false
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\startup_folder_status.json" -Encoding UTF8

Write-Host "[KOS] Startup Folder registrado com sucesso."
Write-Host "[KOS] O K-OS iniciara no proximo login do Windows."
Write-Host "[KOS] Para iniciar agora manualmente, rode:"
Write-Host "powershell -ExecutionPolicy Bypass -File scripts\start_kos_autonomy_scheduler_manual_loop.ps1"
