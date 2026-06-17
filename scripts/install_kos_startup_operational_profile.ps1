$ErrorActionPreference = "Stop";
Set-Location "C:\Users\oi\Desktop\motor-digital";

$StartupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup";
New-Item -ItemType Directory -Force $StartupDir | Out-Null;

$CmdPath = Join-Path $StartupDir "KOS_Startup_Operational_Profile.cmd";
$DesktopCmd = Join-Path ([Environment]::GetFolderPath("Desktop")) "KOS_Startup_Operational_Profile.cmd";

$Cmd = '@echo off
cd /d "C:\Users\oi\Desktop\motor-digital"
powershell -WindowStyle Minimized -ExecutionPolicy Bypass -File "scripts\start_kos_startup_operational_profile.ps1"
';

$Cmd | Set-Content $CmdPath -Encoding ASCII;
$Cmd | Set-Content $DesktopCmd -Encoding ASCII;

$Report = [ordered]@{
  status = "KOS_STARTUP_OPERATIONAL_PROFILE_INSTALLED"
  phase = "66B2"
  startup_cmd = $CmdPath
  desktop_cmd = $DesktopCmd
  script = "scripts\start_kos_startup_operational_profile.ps1"
  production_publish_locked = $true
  paid_ai_locked = $true
  instagram_publish_locked = $true
  browser_logged_account_automation_used = $false
  created_at = (Get-Date).ToUniversalTime().ToString("o")
};

$Report | ConvertTo-Json -Depth 20 | Set-Content "reports\KOS_PHASE66B2_STARTUP_OPERATIONAL_PROFILE_BOOTSTRAP.json" -Encoding UTF8;

Write-Host "[KOS] Startup instalado:";
Write-Host $CmdPath;
Write-Host "[KOS] Atalho criado:";
Write-Host $DesktopCmd;
