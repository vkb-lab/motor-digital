$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

if(!$env:KOS_LOCAL_COWORKER_INTERVAL_SECONDS){
  $env:KOS_LOCAL_COWORKER_INTERVAL_SECONDS="60"
}

if(!$env:KOS_LOCAL_COWORKER_MAX_CYCLES){
  $env:KOS_LOCAL_COWORKER_MAX_CYCLES="0"
}

$interval=[int]$env:KOS_LOCAL_COWORKER_INTERVAL_SECONDS
$max=[int]$env:KOS_LOCAL_COWORKER_MAX_CYCLES
$count=0

Write-Host "[KOS] Local Coworker loop iniciado."
Write-Host "[KOS] Intervalo: $interval segundos."
Write-Host "[KOS] Max cycles: $max"
Write-Host "[KOS] Para parar: CTRL+C"

while($true){
  $count++
  Write-Host "[KOS] Coworker tick $count"
  python scripts\run_phase61a_local_coworker_tick.py

  if($max -gt 0 -and $count -ge $max){
    Write-Host "[KOS] Max cycles atingido. Encerrando."
    break
  }

  Start-Sleep -Seconds $interval
}