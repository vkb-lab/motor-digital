param(
  [int]$IntervalSeconds = 45,
  [int]$Limit = 5,
  [switch]$Once
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

Write-Host "[KOS] Mission Queue Loop iniciado.";
Write-Host "[KOS] IntervalSeconds =" $IntervalSeconds;
Write-Host "[KOS] Limit =" $Limit;
Write-Host "[KOS] Once =" $Once;

while($true){
  $TickStartedAt = (Get-Date).ToUniversalTime().ToString("o");

  try {
    $ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
    $KillEngaged = $false;

    if(Test-Path $ControlPath){
      $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
      if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
        $KillEngaged = $true;
      }
    }

    if($KillEngaged){
      Write-Host "[KOS] Kill Switch engaged. Mission queue loop paused.";
      $ProcessorStatus = [ordered]@{
        status = "KOS_AUTONOMY_MISSION_QUEUE_LOOP_PAUSED_BY_KILL_SWITCH"
        processed_count = 0
        succeeded_count = 0
        failed_count = 0
      };
    } else {
      Write-Host "[KOS] Processing mission queue...";
      $ProcessorRaw = powershell -ExecutionPolicy Bypass -File scripts\process_kos_autonomy_mission_queue.ps1 -Limit $Limit;
      $ProcessorStatus = $ProcessorRaw -join "`n" | ConvertFrom-Json;
    }

    $LoopStatus = [ordered]@{
      status = "KOS_AUTONOMY_MISSION_QUEUE_LOOP_TICK_COMPLETED"
      kill_switch_engaged = [bool]$KillEngaged
      processor_status = $ProcessorStatus.status
      processed_count = $ProcessorStatus.processed_count
      succeeded_count = $ProcessorStatus.succeeded_count
      failed_count = $ProcessorStatus.failed_count
      interval_seconds = $IntervalSeconds
      limit = $Limit
      once = [bool]$Once
      production_publish_locked = $true
      paid_ai_locked = $true
      real_action_executed = $false
      paid_ai_call_executed = $false
      instagram_publish_executed = $false
      browser_logged_account_automation_used = $false
      tick_started_at = $TickStartedAt
      created_at = (Get-Date).ToUniversalTime().ToString("o")
    };

    New-Item -ItemType Directory -Force "local_runtime\kos_autonomy_missions" | Out-Null;
    $LoopStatus | ConvertTo-Json -Depth 50 | Set-Content "local_runtime\kos_autonomy_missions\latest_mission_queue_loop_tick.json" -Encoding UTF8;
  } catch {
    $ErrorStatus = [ordered]@{
      status = "KOS_AUTONOMY_MISSION_QUEUE_LOOP_TICK_FAILED"
      error = $_.Exception.Message
      production_publish_locked = $true
      paid_ai_locked = $true
      instagram_publish_executed = $false
      browser_logged_account_automation_used = $false
      created_at = (Get-Date).ToUniversalTime().ToString("o")
    };

    New-Item -ItemType Directory -Force "local_runtime\kos_autonomy_missions" | Out-Null;
    $ErrorStatus | ConvertTo-Json -Depth 20 | Set-Content "local_runtime\kos_autonomy_missions\latest_mission_queue_loop_tick.json" -Encoding UTF8;
    Write-Host "[KOS] Mission queue loop error:";
    Write-Host $_.Exception.Message;
  }

  if($Once){
    break;
  }

  Start-Sleep -Seconds $IntervalSeconds;
}
