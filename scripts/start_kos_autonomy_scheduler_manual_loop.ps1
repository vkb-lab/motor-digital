$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

if(!$env:KOS_SCHEDULER_INTERVAL_SECONDS){
  $env:KOS_SCHEDULER_INTERVAL_SECONDS="900"
}

if(!$env:KOS_SCHEDULER_MAX_CYCLES){
  $env:KOS_SCHEDULER_MAX_CYCLES="1"
}

$interval=[int]$env:KOS_SCHEDULER_INTERVAL_SECONDS
$max=[int]$env:KOS_SCHEDULER_MAX_CYCLES
$count=0

Write-Host "[KOS] Scheduler manual loop iniciado."
Write-Host "[KOS] Project root:" $ProjectRoot
Write-Host "[KOS] PYTHONPATH:" $env:PYTHONPATH
Write-Host "[KOS] Intervalo segundos:" $interval
Write-Host "[KOS] Max cycles:" $max
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."

while($true){
  $count += 1
  Write-Host "[KOS] Scheduler tick:" $count
  python scripts\run_phase42_scheduler_once.py

  if($LASTEXITCODE -ne 0){
    throw "Scheduler tick falhou."
  }

  if($max -gt 0 -and $count -ge $max){
    Write-Host "[KOS] Scheduler manual loop finalizado por max cycles."
    break
  }

  Start-Sleep -Seconds $interval
}
