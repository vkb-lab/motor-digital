param(
  [ValidateSet("status","health","briefing","evidence","start","stop","restart")]
  [string]$Action="status"
)

$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

$StartConfirm="YES_START_KOS_RUNTIME_LOCAL"
$StopConfirm="YES_STOP_KOS_RUNTIME_LOCAL"
$RestartConfirm="YES_RESTART_KOS_RUNTIME_LOCAL"

function Start-KosRuntime {
  New-Item -ItemType Directory -Force "logs\kaizen\startup" | Out-Null

  $ScriptPath=(Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path
  $LogPath=(Resolve-Path "logs\kaizen\startup").Path + "\runtime_control_background_loop.log"

  $Cmd="Set-Location '$ProjectRoot'; `$env:PYTHONPATH='$ProjectRoot'; `$env:KOS_SCHEDULER_INTERVAL_SECONDS='900'; `$env:KOS_SCHEDULER_MAX_CYCLES='0'; powershell -ExecutionPolicy Bypass -File '$ScriptPath' >> '$LogPath' 2>&1"

  Start-Process powershell.exe -WindowStyle Minimized -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"$Cmd`""

  Write-Host "[KOS] Runtime iniciado em background."
}

function Stop-KosRuntime {
  $procs=Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "start_kos_autonomy_scheduler_manual_loop" }

  if(!$procs){
    Write-Host "[KOS] Nenhum runtime background encontrado."
    return
  }

  foreach($p in $procs){
    Write-Host "[KOS] Stop PID:" $p.ProcessId
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  }

  Write-Host "[KOS] Runtime parado."
}

if($Action -eq "status"){
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}

if($Action -eq "health"){
  python scripts\run_phase44_runtime_health_check.py
  exit 0
}

if($Action -eq "briefing"){
  python scripts\run_phase46_operator_briefing.py
  exit 0
}

if($Action -eq "evidence"){
  python scripts\run_phase48_evidence_ledger.py
  exit 0
}

if($Action -eq "start"){
  $Confirm=(Read-Host "Para iniciar runtime local, digite exatamente YES_START_KOS_RUNTIME_LOCAL").Trim()
  if($Confirm -ne $StartConfirm){
    Write-Host "[KOS] Confirmacao incorreta. Runtime nao iniciado."
    exit 0
  }
  Start-KosRuntime
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}

if($Action -eq "stop"){
  $Confirm=(Read-Host "Para parar runtime local, digite exatamente YES_STOP_KOS_RUNTIME_LOCAL").Trim()
  if($Confirm -ne $StopConfirm){
    Write-Host "[KOS] Confirmacao incorreta. Runtime nao parado."
    exit 0
  }
  Stop-KosRuntime
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}

if($Action -eq "restart"){
  $Confirm=(Read-Host "Para reiniciar runtime local, digite exatamente YES_RESTART_KOS_RUNTIME_LOCAL").Trim()
  if($Confirm -ne $RestartConfirm){
    Write-Host "[KOS] Confirmacao incorreta. Runtime nao reiniciado."
    exit 0
  }
  Stop-KosRuntime
  Start-Sleep -Seconds 2
  Start-KosRuntime
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}
