param(
  [int]$IntervalSeconds = 30,
  [int]$Limit = 20,
  [switch]$Once
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;
$env:PYTHONPATH = $Root;

Write-Host "[KOS] Autonomous Job Runner Loop iniciado.";
Write-Host "[KOS] IntervalSeconds =" $IntervalSeconds;
Write-Host "[KOS] Limit =" $Limit;
Write-Host "[KOS] Once =" $Once;

while($true){
  $TickStartedAt = (Get-Date).ToUniversalTime().ToString("o");

  try {
    $KillRaw = powershell -ExecutionPolicy Bypass -File scripts\kos_autonomy_kill_switch.ps1 -Action status;
    $KillText = $KillRaw -join "`n";
    $Kill = $KillText | ConvertFrom-Json;

    if($Kill.engaged -eq $true){
      Write-Host "[KOS] Kill Switch engaged. Autonomous job loop paused.";
    } else {
      Write-Host "[KOS] Processing autonomous jobs...";
      python scripts\run_phase67b_autonomous_job_runner.py --limit $Limit;
    }

    $LoopStatus = [ordered]@{
      status = "KOS_AUTONOMOUS_JOB_RUNNER_LOOP_TICK_COMPLETED"
      kill_switch_engaged = [bool]$Kill.engaged
      interval_seconds = $IntervalSeconds
      limit = $Limit
      once = [bool]$Once
      real_action_executed = $false
      paid_ai_call_executed = $false
      instagram_publish_executed = $false
      browser_logged_account_automation_used = $false
      tick_started_at = $TickStartedAt
      created_at = (Get-Date).ToUniversalTime().ToString("o")
    };

    New-Item -ItemType Directory -Force "local_runtime\kos_autonomous_jobs" | Out-Null;
    $LoopStatus | ConvertTo-Json -Depth 20 | Set-Content "local_runtime\kos_autonomous_jobs\latest_autonomous_job_runner_loop_tick.json" -Encoding UTF8;
  } catch {
    Write-Host "[KOS] Autonomous job loop error:";
    Write-Host $_.Exception.Message;
  }

  if($Once){
    break;
  }

  Start-Sleep -Seconds $IntervalSeconds;
}
