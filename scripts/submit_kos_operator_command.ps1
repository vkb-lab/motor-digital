param(
  [string]$Text = "registrar comando operacional seguro",
  [string]$CommandId = "",
  [switch]$RunNow
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
if(Test-Path $ControlPath){
  $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
  if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
    throw "Kill Switch engajado. Operator Command Inbox bloqueado."
  }
}

if([string]::IsNullOrWhiteSpace($CommandId)){
  $CommandId = "KOS-OPCMD-" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$SafeCommandId = $CommandId -replace '[^A-Za-z0-9_\-]', '-';

$Inbox = Join-Path $Root "local_runtime\kos_operator_commands\inbox";
$Processed = Join-Path $Root "local_runtime\kos_operator_commands\processed";
New-Item -ItemType Directory -Force $Inbox,$Processed | Out-Null;

$InboxPath = Join-Path $Inbox ($SafeCommandId + ".json");

$OperatorRecord = [ordered]@{
  status = "KOS_OPERATOR_COMMAND_RECEIVED"
  command_id = $SafeCommandId
  text = $Text
  route = "kos_autonomy_command_bridge_67e"
  run_now = [bool]$RunNow
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$OperatorRecord | ConvertTo-Json -Depth 20 | Set-Content $InboxPath -Encoding UTF8;

$BridgeRaw = powershell -ExecutionPolicy Bypass -File scripts\create_kos_autonomy_command.ps1 -CommandId $SafeCommandId -CommandText $Text;
$Bridge = $BridgeRaw -join "`n" | ConvertFrom-Json;

$ProcessedPath = Join-Path $Processed ($SafeCommandId + ".json");

$Result = [ordered]@{
  status = "KOS_OPERATOR_COMMAND_ROUTED"
  command_id = $SafeCommandId
  inbox_path = $InboxPath
  bridge_status = $Bridge.status
  job_id = $Bridge.job_id
  job_path = $Bridge.job_path
  routed_action = $Bridge.routed_action
  run_now = [bool]$RunNow
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

if($RunNow){
  python scripts\run_phase67b_autonomous_job_runner.py --limit 50 | Out-Null;
  $OutPath = Join-Path $Root ("local_runtime\kos_autonomous_jobs\output\" + $SafeCommandId + ".json");
  $MarkerPath = Join-Path $Root ("local_runtime\kos_autonomous_jobs\processed\" + $SafeCommandId + ".json");

  if((Test-Path $OutPath) -and (Test-Path $MarkerPath)){
    $Result.status = "KOS_OPERATOR_COMMAND_EXECUTED"
    $Result.output_path = $OutPath
    $Result.processed_marker = $MarkerPath
  }
}

$Result | ConvertTo-Json -Depth 20 | Set-Content $ProcessedPath -Encoding UTF8;
$Result | ConvertTo-Json -Depth 20;
