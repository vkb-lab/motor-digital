param(
  [ValidateSet("start","stop","status","restart","logs")]
  [string]$Action="status"
)

$ErrorActionPreference="Stop";
$Root=Split-Path -Parent $PSScriptRoot;
Set-Location $Root;

$OutLog="local_runtime\kos_chatgpt_bridge\logs\drop_watcher.out.log";
$ErrLog="local_runtime\kos_chatgpt_bridge\logs\drop_watcher.err.log";

New-Item -ItemType Directory -Force "local_runtime\kos_chatgpt_bridge\runtime","local_runtime\kos_chatgpt_bridge\logs","local_runtime\kos_chatgpt_bridge\drop" | Out-Null;

function NowIso { (Get-Date).ToUniversalTime().ToString("o") }
function JsonOut($x) { $x | ConvertTo-Json -Depth 20 }

function FindWatcher {
  Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "run_phase70d_chatgpt_bridge_drop_watcher.py" -and $_.CommandLine -match "--loop" } |
    Select-Object -First 1
}

function Status {
  $p=FindWatcher;
  if($null -ne $p){
    return [ordered]@{
      status="KOS_CHATGPT_BRIDGE_RUNTIME_RUNNING"
      phase="70E"
      pid=$p.ProcessId
      drop_dir="local_runtime\kos_chatgpt_bridge\drop"
      out_log=$OutLog
      err_log=$ErrLog
      auto_execution_enabled=$false
      operator_review_required=$true
      browser_scraping_enabled=$false
      reads_chatgpt_ui_automatically=$false
      checked_at=NowIso
    }
  }

  return [ordered]@{
    status="KOS_CHATGPT_BRIDGE_RUNTIME_STOPPED"
    phase="70E"
    drop_dir="local_runtime\kos_chatgpt_bridge\drop"
    out_log=$OutLog
    err_log=$ErrLog
    auto_execution_enabled=$false
    operator_review_required=$true
    browser_scraping_enabled=$false
    reads_chatgpt_ui_automatically=$false
    checked_at=NowIso
  }
}

function StartWatcher {
  $p=FindWatcher;
  if($null -ne $p){ return Status }

  $args=@(
    "scripts\run_phase70d_chatgpt_bridge_drop_watcher.py",
    "--loop",
    "--poll-seconds",
    "5",
    "--limit",
    "5"
  );

  Start-Process -FilePath "python" -ArgumentList $args -WorkingDirectory $Root -WindowStyle Minimized -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog | Out-Null;
  Start-Sleep -Seconds 2;
  return Status
}

function StopWatcher {
  $items=Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "run_phase70d_chatgpt_bridge_drop_watcher.py" -and $_.CommandLine -match "--loop" };

  foreach($item in $items){
    Stop-Process -Id $item.ProcessId -Force -ErrorAction SilentlyContinue;
  }

  return [ordered]@{
    status="KOS_CHATGPT_BRIDGE_RUNTIME_STOPPED"
    phase="70E"
    stopped_count=@($items).Count
    auto_execution_enabled=$false
    operator_review_required=$true
    stopped_at=NowIso
  }
}

function Logs {
  $out="";
  $err="";
  if(Test-Path $OutLog){ $out=(Get-Content $OutLog -Tail 60 -Encoding UTF8) -join "`n" }
  if(Test-Path $ErrLog){ $err=(Get-Content $ErrLog -Tail 60 -Encoding UTF8) -join "`n" }

  return [ordered]@{
    status="KOS_CHATGPT_BRIDGE_RUNTIME_LOGS_READY"
    phase="70E"
    stdout_tail=$out
    stderr_tail=$err
    auto_execution_enabled=$false
    operator_review_required=$true
    checked_at=NowIso
  }
}

if($Action -eq "start"){ JsonOut (StartWatcher); exit 0 }
if($Action -eq "stop"){ JsonOut (StopWatcher); exit 0 }
if($Action -eq "restart"){ StopWatcher | Out-Null; JsonOut (StartWatcher); exit 0 }
if($Action -eq "logs"){ JsonOut (Logs); exit 0 }

JsonOut (Status)
