param(
  [string]$RepoPath = "C:\Users\oi\Desktop\motor-digital",
  [int]$Port = 8523
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-KosLog {
  param([string]$Message)
  $logDir = Join-Path $RepoPath "live"
  if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
  $line = ("{0} {1}" -f (Get-Date).ToString("s"), $Message)
  Add-Content -Path (Join-Path $logDir "operator_mode_start.log") -Value $line -Encoding UTF8
}

function Test-KosPort {
  param([int]$CheckPort)
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $result = $client.BeginConnect("127.0.0.1", $CheckPort, $null, $null)
    $ok = $result.AsyncWaitHandle.WaitOne(700, $false)
    if ($ok) { $client.EndConnect($result) | Out-Null }
    $client.Close()
    return $ok
  } catch {
    return $false
  }
}

try {
  Set-Location $RepoPath
  Write-KosLog "K-OS Operator Mode start requested."

  $serverProcesses = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and
    $_.CommandLine -match "streamlit" -and
    $_.CommandLine -match "pages[\\/]+KOS_Operator_Chat.py" -and
    $_.CommandLine -match "--server.port $Port" -and
    $_.CommandLine -match "python"
  })

  if ($serverProcesses.Count -gt 1) {
    $keep = $serverProcesses | Sort-Object ProcessId -Descending | Select-Object -First 1
    $serverProcesses | Where-Object { $_.ProcessId -ne $keep.ProcessId } | ForEach-Object {
      Write-KosLog ("Stopping duplicate Streamlit server PID " + $_.ProcessId)
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
  }

  $launcherProcesses = @(Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and
    $_.CommandLine -match "powershell" -and
    $_.CommandLine -match "streamlit" -and
    $_.CommandLine -match "pages[\\/]+KOS_Operator_Chat.py"
  })

  foreach ($p in $launcherProcesses) {
    if ($p.ProcessId -ne $PID) {
      Write-KosLog ("Stopping visible/old launcher PowerShell PID " + $p.ProcessId)
      Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
  }

  if (!(Test-KosPort -CheckPort $Port)) {
    Write-KosLog "Starting hidden Operator Chat Streamlit server."
    $cmd = "Set-Location `"$RepoPath`"; python -m streamlit run `"pages\KOS_Operator_Chat.py`" --server.port $Port --server.headless true --browser.gatherUsageStats false"
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-Command",$cmd) | Out-Null

    for ($i = 0; $i -lt 30; $i++) {
      Start-Sleep -Milliseconds 500
      if (Test-KosPort -CheckPort $Port) { break }
    }
  } else {
    Write-KosLog "Operator Chat server already running."
  }

  Start-Process ("http://localhost:{0}" -f $Port)
  Write-KosLog "Browser opened to Operator Chat only."
} catch {
  Write-KosLog ("ERROR: " + $_.Exception.Message)
}
