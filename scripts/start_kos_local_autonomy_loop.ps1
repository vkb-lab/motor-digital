$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

if(!$env:KOS_LOCAL_AUTONOMY_INTERVAL_SECONDS){
  $env:KOS_LOCAL_AUTONOMY_INTERVAL_SECONDS="90"
}

if(!$env:KOS_LOCAL_AUTONOMY_MAX_CYCLES){
  $env:KOS_LOCAL_AUTONOMY_MAX_CYCLES="0"
}

$interval=[int]$env:KOS_LOCAL_AUTONOMY_INTERVAL_SECONDS
$max=[int]$env:KOS_LOCAL_AUTONOMY_MAX_CYCLES
$count=0

Write-Host "[KOS] Local Autonomy Loop iniciado."
Write-Host "[KOS] Pipeline: Bridge -> Coworker -> Patch Workspace -> Command Composer"
Write-Host "[KOS] Intervalo: $interval segundos."
Write-Host "[KOS] Max cycles: $max"
Write-Host "[KOS] Para parar: CTRL+C"
Write-Host "[KOS] Este loop NAO executa command drafts."

while($true){
  $count++
  Write-Host "[KOS] Autonomy cycle $count"
  python scripts\run_phase61d_local_autonomy_loop.py

  if($max -gt 0 -and $count -ge $max){
    Write-Host "[KOS] Max cycles atingido. Encerrando."
    break
  }

  Start-Sleep -Seconds $interval
}