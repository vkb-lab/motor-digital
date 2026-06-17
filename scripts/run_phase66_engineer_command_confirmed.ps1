
param(
  [Parameter(Mandatory=$true)]
  [string]$CommandFile,

  [Parameter(Mandatory=$true)]
  [string]$Confirmation
)

$ErrorActionPreference="Stop"

Set-Location "C:\Users\oi\Desktop\motor-digital"
$env:PYTHONPATH="C:\Users\oi\Desktop\motor-digital"

$Required="YES_EXECUTE_K_ATLAS_ENGINEER_COMMAND_LOCAL_ONLY"

if($Confirmation -ne $Required){
  Write-Host "[KOS] Confirmacao invalida. Execucao bloqueada."
  throw "Confirmacao exigida: YES_EXECUTE_K_ATLAS_ENGINEER_COMMAND_LOCAL_ONLY"
}

$Resolved=(Resolve-Path $CommandFile).Path

Write-Host "[KOS] Validando comando staged..."
python scripts\validate_phase66_engineer_command.py -CommandFile $Resolved

if($LASTEXITCODE -ne 0){
  throw "Comando bloqueado pela validacao da Fase 66."
}

Write-Host "[KOS] Git status antes:"
git --no-pager status --short

Write-Host "[KOS] Executando comando aprovado pelo operador..."
powershell -NoProfile -ExecutionPolicy Bypass -File $Resolved

Write-Host "[KOS] Git status depois:"
git --no-pager status --short
