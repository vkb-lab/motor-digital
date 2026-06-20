param()
$ErrorActionPreference = "Continue"
$Root = "C:\Users\oi\Desktop\motor-digital"
$MainPage = "pages\KOS_Operator_Chat.py"
$Port = 8523
$KosPorts = @(8501, 8520, 8521, 8522, 8523)
Set-Location $Root
Write-Host "[KOS] Single Window Operator Mode"
Write-Host "[KOS] Fechando Streamlits K-OS antigos..."
$escapedRoot = [regex]::Escape($Root)
$kosProcesses = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and (($_.CommandLine -match "streamlit" -and $_.CommandLine -match $escapedRoot) -or ($_.CommandLine -match "streamlit" -and $_.CommandLine -match "pages\\KOS_") -or ($_.CommandLine -match "streamlit" -and $_.CommandLine -match "KOS_Operator_Chat")) }
foreach ($proc in $kosProcesses) { try { Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host ("[KOS] Processo encerrado: " + $proc.ProcessId) } catch {} }
foreach ($p in $KosPorts) { $listeners = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue; foreach ($listener in $listeners) { $owner = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $listener.OwningProcess) -ErrorAction SilentlyContinue; if ($owner -and $owner.CommandLine -and ($owner.CommandLine -match "streamlit" -or $owner.CommandLine -match $escapedRoot)) { try { Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue; Write-Host ("[KOS] Porta liberada: " + $p) } catch {} } } }
Start-Sleep -Seconds 1
Write-Host "[KOS] Abrindo somente o Operator Chat na porta 8523..."
$runCommand = "cd '$Root'; python -m streamlit run '$MainPage' --server.port $Port --server.headless true --browser.gatherUsageStats false"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command ""$runCommand"""
Start-Sleep -Seconds 4
Start-Process ("http://localhost:" + $Port)
Write-Host "[KOS] Pronto. Tela unica aberta: http://localhost:8523"
