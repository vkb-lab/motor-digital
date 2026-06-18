param(
  [string]$MissionId = "",
  [string]$MissionText = "executar missao operacional segura",
  [string[]]$Objectives = @(
    "registrar objetivo operacional 1",
    "registrar objetivo operacional 2"
  ),
  [switch]$RunNow
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
if(Test-Path $ControlPath){
  $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
  if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
    throw "Kill Switch engajado. Mission Runner bloqueado."
  }
}

if([string]::IsNullOrWhiteSpace($MissionId)){
  $MissionId = "KOS-MISSION-" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$SafeMissionId = $MissionId -replace '[^A-Za-z0-9_\-]', '-';

$MissionDir = Join-Path $Root "local_runtime\kos_autonomy_missions";
New-Item -ItemType Directory -Force $MissionDir | Out-Null;

$MissionPath = Join-Path $MissionDir ($SafeMissionId + ".json");

$Mission = [ordered]@{
  status = "KOS_AUTONOMY_MISSION_RECEIVED"
  mission_id = $SafeMissionId
  mission_text = $MissionText
  objectives = $Objectives
  run_now = [bool]$RunNow
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$Mission | ConvertTo-Json -Depth 30 | Set-Content $MissionPath -Encoding UTF8;

$BatchRaw = powershell -ExecutionPolicy Bypass -File scripts\submit_kos_operator_command_batch.ps1 -BatchId $SafeMissionId -Commands $Objectives -RunNow:$RunNow;
$Batch = $BatchRaw -join "`n" | ConvertFrom-Json;

$FinalStatus = if($Batch.status -eq "KOS_OPERATOR_COMMAND_BATCH_COMPLETED") {
  "KOS_AUTONOMY_MISSION_COMPLETED"
} else {
  "KOS_AUTONOMY_MISSION_PARTIAL_OR_FAILED"
};

$Result = [ordered]@{
  status = $FinalStatus
  mission_id = $SafeMissionId
  mission_path = $MissionPath
  mission_text = $MissionText
  objective_count = $Objectives.Count
  batch_status = $Batch.status
  batch_id = $Batch.batch_id
  succeeded_count = $Batch.succeeded_count
  failed_count = $Batch.failed_count
  items = $Batch.items
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$Result | ConvertTo-Json -Depth 40 | Set-Content $MissionPath -Encoding UTF8;
$Result | ConvertTo-Json -Depth 40;
