$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = "C:\Users\oi\Desktop\motor-digital"
$ScriptPath = Join-Path $ProjectRoot "ops\run_ksocial_gateway_local.ps1"
$TaskName = "K-Atlas K-Social Gateway Local"

if (-not (Test-Path $ScriptPath)) {
    throw "Script local nao encontrado: $ScriptPath"
}

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 10 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null

Write-Host "Tarefa instalada:"
Write-Host $TaskName
Write-Host "O K-Social Gateway vai iniciar automaticamente quando o Windows fizer login."