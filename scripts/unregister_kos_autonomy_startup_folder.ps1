$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot

$EntryName="KOS-Autonomy-Scheduler-Local.cmd"
$StartupFolder=[Environment]::GetFolderPath("Startup")
$EntryPath=Join-Path $StartupFolder $EntryName

Write-Host "[KOS] Removendo Startup Folder entry:" $EntryPath

if(Test-Path $EntryPath){
  Remove-Item -Force $EntryPath
  Write-Host "[KOS] Startup entry removido."
} else {
  Write-Host "[KOS] Startup entry nao encontrado."
}

New-Item -ItemType Directory -Force "local_runtime\kaizen" | Out-Null

$Status=[ordered]@{
  status="STARTUP_FOLDER_ENTRY_UNREGISTERED_OR_NOT_FOUND"
  entry_path=$EntryPath
  requires_admin=$false
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\startup_folder_status.json" -Encoding UTF8
