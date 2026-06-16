$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"

$TaskName="KOS-Autonomy-Scheduler-Local"

Write-Host "[KOS] Removendo tarefa Windows:" $TaskName

$Task=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if($Task){
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "[KOS] Tarefa removida."
} else {
  Write-Host "[KOS] Tarefa nao encontrada."
}

New-Item -ItemType Directory -Force "local_runtime\kaizen" | Out-Null

$Status=[ordered]@{
  status="WINDOWS_TASK_UNREGISTERED_OR_NOT_FOUND"
  task_name=$TaskName
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\windows_task_status.json" -Encoding UTF8
