param(
  [ValidateSet("status","engage","disengage")]
  [string]$Action = "status",

  [string]$Reason = "operator requested",

  [switch]$RestartRuntime
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlDir = Join-Path $Root "local_runtime\kos_control";
$SwitchPath = Join-Path $ControlDir "AUTONOMY_KILL_SWITCH.json";
New-Item -ItemType Directory -Force $ControlDir | Out-Null;

$RolesToStop = @(
  "scheduler_tick",
  "local_autonomy_loop",
  "engineer_handoff_queue_loop",
  "queue_approval_executor_loop",
  "scheduler_supervisor"
);

function Write-KosSwitchState {
  param(
    [string]$Status,
    [bool]$Engaged,
    [string]$Reason
  )

  $Payload = [ordered]@{
    status = $Status
    engaged = $Engaged
    phase = "67A"
    reason = $Reason
    roles_blocked = $RolesToStop
    requires_manual_disengage = $true
    production_publish_locked = $true
    paid_ai_locked = $true
    real_action_executed = $true
    paid_ai_call_executed = $false
    instagram_publish_executed = $false
    browser_logged_account_automation_used = $false
    created_at = (Get-Date).ToUniversalTime().ToString("o")
  };

  $Payload | ConvertTo-Json -Depth 20 | Set-Content $SwitchPath -Encoding UTF8;
  return $Payload;
}

function Read-KosSwitchState {
  if(Test-Path $SwitchPath){
    return Get-Content $SwitchPath -Encoding UTF8 | ConvertFrom-Json;
  }

  return [ordered]@{
    status = "KOS_AUTONOMY_KILL_SWITCH_DISENGAGED"
    engaged = $false
    phase = "67A"
    switch_path = $SwitchPath
    exists = $false
    created_at = (Get-Date).ToUniversalTime().ToString("o")
  };
}

if($Action -eq "engage"){
  Write-Host "[KOS] ENGAGING AUTONOMY KILL SWITCH...";
  $State = Write-KosSwitchState -Status "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" -Engaged $true -Reason $Reason;

  $RuntimeRaw = powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action status;
  $RuntimeText = $RuntimeRaw -join "`n";
  $Runtime = $RuntimeText | ConvertFrom-Json;

  foreach($Proc in $Runtime.runtime_processes){
    if($RolesToStop -contains $Proc.role){
      if($Proc.pid -ne $PID){
        Write-Host "[KOS] Stopping role:" $Proc.role "pid:" $Proc.pid;
        Stop-Process -Id $Proc.pid -Force -ErrorAction SilentlyContinue;
      }
    }
  }

  $State | ConvertTo-Json -Depth 20;
  exit 0;
}

if($Action -eq "disengage"){
  Write-Host "[KOS] DISENGAGING AUTONOMY KILL SWITCH...";
  $State = Write-KosSwitchState -Status "KOS_AUTONOMY_KILL_SWITCH_DISENGAGED" -Engaged $false -Reason $Reason;

  if($RestartRuntime){
    Write-Host "[KOS] Restarting startup operational profile...";
    powershell -ExecutionPolicy Bypass -File scripts\start_kos_startup_operational_profile.ps1;
  }

  $State | ConvertTo-Json -Depth 20;
  exit 0;
}

$State = Read-KosSwitchState;
[ordered]@{
  status = "KOS_AUTONOMY_KILL_SWITCH_STATUS"
  engaged = [bool]$State.engaged
  state = $State
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json -Depth 20;
