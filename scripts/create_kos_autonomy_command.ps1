param(
  [string]$CommandText = "registrar comando autonomo seguro",
  [string]$CommandId = ""
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
if(Test-Path $ControlPath){
  $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
  if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
    throw "Kill Switch engajado. Command Bridge bloqueado."
  }
}

if([string]::IsNullOrWhiteSpace($CommandId)){
  $CommandId = "KOS-CMD-" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$SafeCommandId = $CommandId -replace '[^A-Za-z0-9_\-]', '-';

$CommandDir = Join-Path $Root "local_runtime\kos_autonomy_commands";
New-Item -ItemType Directory -Force $CommandDir | Out-Null;

$CommandPath = Join-Path $CommandDir ($SafeCommandId + ".json");

$CommandRecord = [ordered]@{
  status = "KOS_AUTONOMY_COMMAND_RECEIVED"
  command_id = $SafeCommandId
  command_text = $CommandText
  routed_action = "write_json_report"
  source = "kos_autonomy_command_bridge_67e"
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$CommandRecord | ConvertTo-Json -Depth 20 | Set-Content $CommandPath -Encoding UTF8;

$JobRaw = powershell -ExecutionPolicy Bypass -File scripts\create_kos_autonomous_job.ps1 -JobId $SafeCommandId -Message $CommandText -Scope "autonomy_command_bridge_67e";
$Job = $JobRaw -join "`n" | ConvertFrom-Json;

[ordered]@{
  status = "KOS_AUTONOMY_COMMAND_ROUTED_TO_JOB"
  command_id = $SafeCommandId
  command_path = $CommandPath
  job_id = $Job.job_id
  job_path = $Job.job_path
  routed_action = $Job.action
  created_at = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json -Depth 20;
