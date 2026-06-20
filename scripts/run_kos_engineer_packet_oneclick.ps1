param(
  [switch]$FromClipboard,
  [string]$File = "",
  [switch]$NoQueueTick
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

if(-not $FromClipboard -and [string]::IsNullOrWhiteSpace($File)){
  throw "Use -FromClipboard ou -File."
}

if($FromClipboard){
  $IntakeRaw = powershell -ExecutionPolicy Bypass -File scripts\submit_kos_engineer_command_intake.ps1 -FromClipboard;
} else {
  $IntakeRaw = powershell -ExecutionPolicy Bypass -File scripts\submit_kos_engineer_command_intake.ps1 -File $File;
}

$Intake = ($IntakeRaw -join "`n") | ConvertFrom-Json;

if($Intake.status -ne "KOS_ENGINEER_COMMAND_INTAKE_STAGED"){
  $Result = [ordered]@{
    status="KOS_ENGINEER_PACKET_ONECLICK_BLOCKED_AT_INTAKE"
    phase="69K"
    intake_status=$Intake.status
    intake_reason=$Intake.reason
    auto_execution_enabled=$false
    created_at=(Get-Date).ToUniversalTime().ToString("o")
  };
  $Result | ConvertTo-Json -Depth 20 | Set-Content "local_runtime\kos_engineer_command_intake\latest_oneclick_result.json" -Encoding UTF8;
  $Result | ConvertTo-Json -Depth 20;
  exit 0;
}

$PacketId = $Intake.packet_id;
$StagedPath = "local_runtime\kos_engineer_command_intake\staged\$PacketId.json";

if(-not (Test-Path $StagedPath)){
  throw "Pacote staged nao encontrado: $StagedPath"
}

$PromotionRaw = python scripts\run_phase69j_engineer_packet_promotion_bridge.py --packet-file $StagedPath;
$Promotion = ($PromotionRaw -join "`n") | ConvertFrom-Json;

$QueueTickExecuted = $false;
$QueueTickStatus = "SKIPPED";

if(-not $NoQueueTick -and (Test-Path "scripts\run_phase66b_engineer_handoff_queue.py")){
  $QueueRaw = python scripts\run_phase66b_engineer_handoff_queue.py;
  $QueueTickExecuted = $true;
  $QueueTickStatus = "EXECUTED";
}

$Result = [ordered]@{
  status="KOS_ENGINEER_PACKET_ONECLICK_COMPLETED"
  phase="69K"
  packet_id=$PacketId
  intake_status=$Intake.status
  promotion_status=$Promotion.status
  handoff_inbox_file=$Promotion.handoff_inbox_file
  queue_tick_executed=$QueueTickExecuted
  queue_tick_status=$QueueTickStatus
  auto_execution_enabled=$false
  operator_review_required=$true
  execution_requires_existing_approval_pipeline=$true
  production_publish_locked=$true
  paid_ai_locked=$true
  instagram_publish_executed=$false
  browser_logged_account_automation_used=$false
  real_action_executed=$false
  created_at=(Get-Date).ToUniversalTime().ToString("o")
};

$Result | ConvertTo-Json -Depth 30 | Set-Content "local_runtime\kos_engineer_command_intake\latest_oneclick_result.json" -Encoding UTF8;
$Result | ConvertTo-Json -Depth 30;
