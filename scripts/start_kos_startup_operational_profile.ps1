$ErrorActionPreference = "Continue";
Set-Location "C:\Users\oi\Desktop\motor-digital";
$env:PYTHONPATH = "C:\Users\oi\Desktop\motor-digital";

$LogDir = "local_runtime\kos_startup_profile";
New-Item -ItemType Directory -Force $LogDir | Out-Null;
$LogPath = Join-Path $LogDir "startup_profile_events.jsonl";

function Write-KosEvent($Stage, $Message, $Data) {
  $Payload = [ordered]@{
    stage = $Stage
    message = $Message
    data = $Data
    created_at = (Get-Date).ToUniversalTime().ToString("o")
  };
  $Payload | ConvertTo-Json -Depth 20 -Compress | Add-Content $LogPath -Encoding UTF8;
  Write-Host "[KOS][$Stage] $Message";
}

function Test-PortOpen($Port) {
  $Conn = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port } | Select-Object -First 1;
  return ($null -ne $Conn);
}

function Start-StreamlitIfMissing($Port, $AppPath, $Name) {
  if (Test-PortOpen $Port) {
    Write-KosEvent "SKIP_PORT_ACTIVE" "$Name ja esta ativo" @{port=$Port; app=$AppPath};
    return;
  }

  if (-not (Test-Path $AppPath)) {
    Write-KosEvent "SKIP_APP_MISSING" "$Name nao iniciado: app ausente" @{port=$Port; app=$AppPath};
    return;
  }

  Write-KosEvent "START_STREAMLIT" "Iniciando $Name" @{port=$Port; app=$AppPath};

  Start-Process powershell -WindowStyle Minimized -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    "cd 'C:\Users\oi\Desktop\motor-digital'; `$env:PYTHONPATH='C:\Users\oi\Desktop\motor-digital'; python -m streamlit run '$AppPath' --server.port $Port"
  );
}

function Start-LoopIfMissing($Pattern, $ScriptPath, $Name) {
  $Existing = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like $Pattern } | Select-Object -First 1;

  if ($Existing) {
    Write-KosEvent "SKIP_LOOP_ACTIVE" "$Name ja esta ativo" @{pid=$Existing.ProcessId; script=$ScriptPath};
    return;
  }

  if (-not (Test-Path $ScriptPath)) {
    Write-KosEvent "SKIP_LOOP_MISSING" "$Name nao iniciado: script ausente" @{script=$ScriptPath};
    return;
  }

  Write-KosEvent "START_LOOP" "Iniciando $Name" @{script=$ScriptPath};

  Start-Process powershell -WindowStyle Minimized -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $ScriptPath
  );
}

function Ensure-SchedulerSupervisor() {
  $SupervisorDir = "local_runtime\kos_runtime_control";
  New-Item -ItemType Directory -Force $SupervisorDir | Out-Null;

  $SupervisorPath = Join-Path $SupervisorDir "start_kos_autonomy_scheduler_manual_loop.ps1.supervisor.ps1";

  if (-not (Test-Path $SupervisorPath)) {
    $Lines = @(
      '$ErrorActionPreference = "Continue";',
      'Set-Location "C:\Users\oi\Desktop\motor-digital";',
      'Write-Host "[KOS] Runtime scheduler supervisor iniciado."; ',
      'while($true){',
      '  try {',
      '    Write-Host "[KOS] Scheduler tick iniciado."; ',
      '    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\start_kos_autonomy_scheduler_manual_loop.ps1";',
      '    Write-Host "[KOS] Scheduler tick finalizado."; ',
      '  } catch {',
      '    Write-Host "[KOS] Erro no scheduler tick:";',
      '    Write-Host $_.Exception.Message;',
      '  }',
      '  Start-Sleep -Seconds 60;',
      '}'
    );
    $Lines | Set-Content $SupervisorPath -Encoding UTF8;
    Write-KosEvent "SUPERVISOR_CREATED" "Scheduler supervisor criado" @{path=$SupervisorPath};
  }

  Start-LoopIfMissing "*start_kos_autonomy_scheduler_manual_loop.ps1.supervisor.ps1*" $SupervisorPath "scheduler_supervisor";
}

Write-KosEvent "START" "Startup Operational Profile iniciado" @{root="C:\Users\oi\Desktop\motor-digital"};

Start-StreamlitIfMissing 8501 "app.py" "K-Atlas OS principal";
Start-StreamlitIfMissing 8507 "local_runtime\operator_command_bridge\operator_bridge_app.py" "Command Bridge";
Start-StreamlitIfMissing 8512 "pages\KOS_Local_Review_Inbox.py" "Review Inbox";
Start-StreamlitIfMissing 8514 "pages\KOS_Engineer_Handoff_Bridge.py" "Engineer Handoff Bridge";
Start-StreamlitIfMissing 8515 "pages\KOS_Engineer_Handoff_Queue.py" "Engineer Handoff Queue";

Start-LoopIfMissing "*start_kos_local_autonomy_loop.ps1*" "scripts\start_kos_local_autonomy_loop.ps1" "local_autonomy_loop";
Start-LoopIfMissing "*start_kos_engineer_handoff_queue_loop.ps1*" "scripts\start_kos_engineer_handoff_queue_loop.ps1" "engineer_handoff_queue_loop";

Ensure-SchedulerSupervisor;

Start-Sleep -Seconds 8;

$Ports = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in @(8501,8507,8512,8514,8515) } | Select-Object LocalPort,OwningProcess,State | Sort-Object LocalPort);
$RuntimeRaw = powershell -ExecutionPolicy Bypass -File scripts\kos_runtime_control.ps1 -Action status | Out-String;
$GitStatus = git --no-pager status --short | Out-String;

$Status = [ordered]@{
  status = "KOS_STARTUP_OPERATIONAL_PROFILE_COMPLETED"
  ports = $Ports
  runtime_status_raw = $RuntimeRaw
  git_status = $GitStatus
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_locked = $true
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$StatusPath = Join-Path $LogDir "latest_startup_profile_status.json";
$Status | ConvertTo-Json -Depth 30 | Set-Content $StatusPath -Encoding UTF8;

Write-KosEvent "DONE" "Startup Operational Profile concluido" @{status_path=$StatusPath};

Write-Host "[KOS] Portas principais:";
$Ports | Format-Table -AutoSize;

Write-Host "[KOS] Runtime:";
Write-Host $RuntimeRaw;

Write-Host "[KOS] Git:";
Write-Host $GitStatus;
