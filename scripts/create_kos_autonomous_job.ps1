param(
  [string]$JobId = "",
  [string]$Message = "operator requested autonomous job",
  [string]$Scope = "local_safe_write_only"
)

$ErrorActionPreference = "Stop";
$Root = Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$ControlPath = Join-Path $Root "local_runtime\kos_control\AUTONOMY_KILL_SWITCH.json";
if(Test-Path $ControlPath){
  $Kill = Get-Content $ControlPath -Encoding UTF8 | ConvertFrom-Json;
  if($Kill.status -eq "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"){
    throw "Kill Switch engajado. Intake bloqueado."
  }
}

if([string]::IsNullOrWhiteSpace($JobId)){
  $JobId = "KOS-JOB-" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$SafeJobId = $JobId -replace '[^A-Za-z0-9_\-]', '-';
$Inbox = Join-Path $Root "local_runtime\kos_autonomous_jobs\inbox";
New-Item -ItemType Directory -Force $Inbox | Out-Null;

$TmpPath = Join-Path $Inbox ($SafeJobId + ".tmp.json");
$FinalPath = Join-Path $Inbox ($SafeJobId + ".json");

$Job = [ordered]@{
  status = "PENDING"
  job_id = $SafeJobId
  action = "write_json_report"
  output_relpath = "local_runtime/kos_autonomous_jobs/output/$SafeJobId.json"
  payload = [ordered]@{
    message = $Message
    scope = $Scope
    source = "kos_autonomous_job_intake_67d"
  }
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_executed = $false
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
}

$Job | ConvertTo-Json -Depth 20 | Set-Content $TmpPath -Encoding UTF8;
Move-Item $TmpPath $FinalPath -Force;

[ordered]@{
  status = "KOS_AUTONOMOUS_JOB_INTAKE_CREATED"
  job_id = $SafeJobId
  job_path = $FinalPath
  output_relpath = $Job.output_relpath
  action = $Job.action
  created_at = (Get-Date).ToUniversalTime().ToString("o")
} | ConvertTo-Json -Depth 20;
