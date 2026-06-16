$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"

$TaskName="KOS-Autonomy-Scheduler-Local"
$Required="YES_REGISTER_KOS_247_LOCAL_ONLY"

Write-Host "[KOS] Registro de tarefa Windows para K-OS 24/7 local."
Write-Host "[KOS] Esta tarefa roda apenas localmente no logon do Windows."
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."
Write-Host "[KOS] Task:" $TaskName

$Confirm=(Read-Host "Para registrar, digite exatamente YES_REGISTER_KOS_247_LOCAL_ONLY").Trim()

if($Confirm -ne $Required){
  Write-Host "[KOS] Confirmacao incorreta. Nenhuma tarefa foi registrada."
  exit 0
}

$ScriptPath=(Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path

$Command = "`$env:KOS_SCHEDULER_INTERVAL_SECONDS='900'; `$env:KOS_SCHEDULER_MAX_CYCLES='0'; & `"$ScriptPath`""

$Action=New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command $Command"
$Trigger=New-ScheduledTaskTrigger -AtLogOn
$Settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "K-OS autonomy scheduler local safe loop" -Force | Out-Null

New-Item -ItemType Directory -Force "local_runtime\kaizen" | Out-Null

$Status=[ordered]@{
  status="WINDOWS_TASK_REGISTERED"
  task_name=$TaskName
  script=$ScriptPath
  interval_seconds=900
  max_cycles=0
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\windows_task_status.json" -Encoding UTF8

Write-Host "[KOS] Tarefa registrada com sucesso."
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName,State
