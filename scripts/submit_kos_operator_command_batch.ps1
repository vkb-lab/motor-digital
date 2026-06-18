param(
  [string]$BatchId = "",
  [string[]]$Commands = @(
    "registrar healthcheck operacional",
    "registrar status de autonomia segura"
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
    throw "Kill Switch engajado. Batch bloqueado."
  }
}

if([string]::IsNullOrWhiteSpace($BatchId)){
  $BatchId = "KOS-BATCH-" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$SafeBatchId = $BatchId -replace '[^A-Za-z0-9_\-]', '-';
$BatchDir = Join-Path $Root "local_runtime\kos_operator_commands\batches";
New-Item -ItemType Directory -Force $BatchDir | Out-Null;

$Items = @();
$Index = 0;

foreach($Text in $Commands){
  $Index += 1;
  $CommandId = "$SafeBatchId-CMD$Index";

  $SubmitRaw = powershell -ExecutionPolicy Bypass -File scripts\submit_kos_operator_command.ps1 -CommandId $CommandId -Text $Text -RunNow:$RunNow;
  $Submit = $SubmitRaw -join "`n" | ConvertFrom-Json;

  $Items += [ordered]@{
    command_id = $CommandId
    text = $Text
    submit_status = $Submit.status
    bridge_status = $Submit.bridge_status
    routed_action = $Submit.routed_action
    job_id = $Submit.job_id
    output_path = $Submit.output_path
    processed_marker = $Submit.processed_marker
  };
}

$Succeeded = @($Items | Where-Object { $_.submit_status -eq "KOS_OPERATOR_COMMAND_EXECUTED" -or $_.submit_status -eq "KOS_OPERATOR_COMMAND_ROUTED" });
$Failed = @($Items | Where-Object { $_.submit_status -ne "KOS_OPERATOR_COMMAND_EXECUTED" -and $_.submit_status -ne "KOS_OPERATOR_COMMAND_ROUTED" });

$Batch = [ordered]@{
  status = if($Failed.Count -eq 0) { "KOS_OPERATOR_COMMAND_BATCH_COMPLETED" } else { "KOS_OPERATOR_COMMAND_BATCH_PARTIAL_OR_FAILED" }
  batch_id = $SafeBatchId
  run_now = [bool]$RunNow
  total_count = $Items.Count
  succeeded_count = $Succeeded.Count
  failed_count = $Failed.Count
  items = $Items
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$BatchPath = Join-Path $BatchDir ($SafeBatchId + ".json");
$Batch | ConvertTo-Json -Depth 30 | Set-Content $BatchPath -Encoding UTF8;
$Batch | ConvertTo-Json -Depth 30;
