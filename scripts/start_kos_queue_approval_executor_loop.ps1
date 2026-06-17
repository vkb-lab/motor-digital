$ErrorActionPreference = "Continue";
Set-Location "C:\Users\oi\Desktop\motor-digital";
$env:PYTHONPATH = "C:\Users\oi\Desktop\motor-digital";
$Interval = 30;
if($env:KOS_QUEUE_APPROVAL_EXECUTOR_INTERVAL_SECONDS){
  try { $Interval = [int]$env:KOS_QUEUE_APPROVAL_EXECUTOR_INTERVAL_SECONDS } catch { $Interval = 30 }
}
Write-Host "[KOS] Queue Approval Executor Loop iniciado.";
Write-Host "[KOS] Approval dir: local_runtime\kos_engineer_handoff\approvals";
while($true){
  try {
    python scripts\run_phase66c_queue_approval_executor.py;
  } catch {
    Write-Host "[KOS] Erro no Queue Approval Executor:";
    Write-Host $_.Exception.Message;
  }
  Start-Sleep -Seconds $Interval;
}
