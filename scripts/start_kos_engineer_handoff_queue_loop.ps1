
$ErrorActionPreference="Stop"

Set-Location "C:\Users\oi\Desktop\motor-digital"
$env:PYTHONPATH="C:\Users\oi\Desktop\motor-digital"

if(!$env:KOS_ENGINEER_HANDOFF_QUEUE_INTERVAL_SECONDS){
  $env:KOS_ENGINEER_HANDOFF_QUEUE_INTERVAL_SECONDS="30"
}

$interval=[int]$env:KOS_ENGINEER_HANDOFF_QUEUE_INTERVAL_SECONDS

Write-Host "[KOS] Engineer Handoff Queue Loop iniciado."
Write-Host "[KOS] Inbox: local_runtime\kos_engineer_handoff\inbox"
Write-Host "[KOS] Este loop stageia e valida. Execucao continua exigindo confirmacao humana."
Write-Host "[KOS] Para parar: CTRL+C"

while($true){
  python scripts\run_phase66b_engineer_handoff_queue.py
  Start-Sleep -Seconds $interval
}
