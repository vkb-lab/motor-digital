param(
  [string]$MissionId = "",
  [string]$MissionText = "missao segura em fila",
  [string[]]$Objectives = @(
    "registrar objetivo de fila 1",
    "registrar objetivo de fila 2"
  )
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
if(Test-Path $ControlPath){
  $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
  if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
    throw "Kill Switch engajado. Submit de mission queue bloqueado."
  }
}

if([string]::IsNullOrWhiteSpace($MissionId)){
  $MissionId = "KOS-MISSION-QUEUE-" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$SafeMissionId = $MissionId -replace '[^A-Za-z0-9_\-]', '-';

$QueueDir = Join-Path $Root "local_runtime\kos_autonomy_missions\queue";
New-Item -ItemType Directory -Force $QueueDir | Out-Null;

$TmpPath = Join-Path $QueueDir ($SafeMissionId + ".tmp.json");
$FinalPath = Join-Path $QueueDir ($SafeMissionId + ".json");

$Mission = [ordered]@{
  status = "KOS_AUTONOMY_MISSION_QUEUED"
  mission_id = $SafeMissionId
  mission_text = $MissionText
  objectives = $Objectives
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$Mission | ConvertTo-Json -Depth 30 | Set-Content $TmpPath -Encoding UTF8;
Move-Item $TmpPath $FinalPath -Force;

[ordered]@{
  status = "KOS_AUTONOMY_MISSION_QUEUE_CREATED"
  mission_id = $SafeMissionId
  mission_path = $FinalPath
  objective_count = $Objectives.Count
  created_at = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json -Depth 20;
