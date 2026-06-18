param(
  [int]$Limit = 5
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
if(Test-Path $ControlPath){
  $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
  if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
    throw "Kill Switch engajado. Mission Queue Processor bloqueado."
  }
}

$QueueDir = Join-Path $Root "local_runtime\kos_autonomy_missions\queue";
$ProcessedDir = Join-Path $Root "local_runtime\kos_autonomy_missions\processed";
$FailedDir = Join-Path $Root "local_runtime\kos_autonomy_missions\failed";

New-Item -ItemType Directory -Force $QueueDir,$ProcessedDir,$FailedDir | Out-Null;

$Files = Get-ChildItem $QueueDir -Filter "*.json" -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -notlike "*.tmp.json" } |
  Sort-Object LastWriteTime |
  Select-Object -First $Limit;

$Items = @();

foreach($File in $Files){
  try {
    $Mission = Get-Content $File.FullName -Encoding UTF8 | ConvertFrom-Json;

    $MissionId = [string]$Mission.mission_id;
    $MissionText = [string]$Mission.mission_text;
    $Objectives = @($Mission.objectives);

    $RunRaw = powershell -ExecutionPolicy Bypass -File scripts\run_kos_autonomy_mission.ps1 -MissionId $MissionId -MissionText $MissionText -Objectives $Objectives -RunNow;
    $Run = $RunRaw -join "`n" | ConvertFrom-Json;

    $Result = [ordered]@{
      status = if($Run.status -eq "KOS_AUTONOMY_MISSION_COMPLETED") { "KOS_AUTONOMY_MISSION_QUEUE_PROCESSED" } else { "KOS_AUTONOMY_MISSION_QUEUE_FAILED" }
      mission_id = $MissionId
      mission_status = $Run.status
      batch_status = $Run.batch_status
      objective_count = $Run.objective_count
      succeeded_count = $Run.succeeded_count
      failed_count = $Run.failed_count
      source_queue_file = $File.FullName
      production_publish_locked = $true
      paid_ai_locked = $true
      instagram_publish_executed = $false
      browser_logged_account_automation_used = $false
      created_at = (Get-Date).ToUniversalTime().ToString("o")
    };

    if($Result.status -eq "KOS_AUTONOMY_MISSION_QUEUE_PROCESSED"){
      $ResultPath = Join-Path $ProcessedDir ($MissionId + ".json");
      $Result | ConvertTo-Json -Depth 40 | Set-Content $ResultPath -Encoding UTF8;
      Move-Item $File.FullName (Join-Path $ProcessedDir ($MissionId + "_source.json")) -Force;
    } else {
      $ResultPath = Join-Path $FailedDir ($MissionId + ".json");
      $Result | ConvertTo-Json -Depth 40 | Set-Content $ResultPath -Encoding UTF8;
      Move-Item $File.FullName (Join-Path $FailedDir ($MissionId + "_source.json")) -Force;
    }

    $Items += $Result;
  } catch {
    $Fail = [ordered]@{
      status = "KOS_AUTONOMY_MISSION_QUEUE_FAILED"
      mission_id = $File.BaseName
      error = $_.Exception.Message
      source_queue_file = $File.FullName
      production_publish_locked = $true
      paid_ai_locked = $true
      instagram_publish_executed = $false
      browser_logged_account_automation_used = $false
      created_at = (Get-Date).ToUniversalTime().ToString("o")
    };

    $Fail | ConvertTo-Json -Depth 20 | Set-Content (Join-Path $FailedDir ($File.BaseName + ".json")) -Encoding UTF8;
    Move-Item $File.FullName (Join-Path $FailedDir ($File.BaseName + "_source.json")) -Force;
    $Items += $Fail;
  }
}

$Succeeded = @($Items | Where-Object { $_.status -eq "KOS_AUTONOMY_MISSION_QUEUE_PROCESSED" });
$Failed = @($Items | Where-Object { $_.status -ne "KOS_AUTONOMY_MISSION_QUEUE_PROCESSED" });

$Status = [ordered]@{
  status = "KOS_AUTONOMY_MISSION_QUEUE_PROCESSOR_STATUS"
  processed_count = $Items.Count
  succeeded_count = $Succeeded.Count
  failed_count = $Failed.Count
  items = $Items
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$Status | ConvertTo-Json -Depth 50 | Set-Content "local_runtime\kos_autonomy_missions\latest_queue_processor_status.json" -Encoding UTF8;
$Status | ConvertTo-Json -Depth 50;
