param(
    [switch]$Approve,
    [switch]$Install
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

cd "C:\Users\oi\Desktop\motor-digital"

if (Test-Path ".\venv\Scripts\python.exe") {
    $Python = ".\venv\Scripts\python.exe"
} elseif (Test-Path ".\.venv\Scripts\python.exe") {
    $Python = ".\.venv\Scripts\python.exe"
} else {
    python -m venv venv
    $Python = ".\venv\Scripts\python.exe"
}

$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

Write-Host "K-Atlas Mission Pipeline Runner"
Write-Host "Modo: gerar -> converter -> instalar localmente"
Write-Host ""

if (-not $Approve) {
    Write-Host "Dry-run apenas. Para instalar, use: -Approve -Install"
    & $Python -m k_atlas.core.mission_pipeline_runner.run_demo
    exit 0
}

Write-Host "Aprovacao humana detectada."

if (Test-Path ".\ops\run_mission_pack_generator_demo.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\run_mission_pack_generator_demo.ps1"
} elseif (Test-Path ".\ops\generate_mission_pack_demo.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\generate_mission_pack_demo.ps1"
} else {
    Write-Host "Script de geracao de mission pack nao encontrado. Seguindo com componentes disponiveis."
}

if (Test-Path ".\ops\run_mission_pack_bridge_demo.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\run_mission_pack_bridge_demo.ps1"
} elseif (Test-Path ".\ops\bridge_latest_mission_pack.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\bridge_latest_mission_pack.ps1"
} else {
    Write-Host "Script de bridge nao encontrado. Seguindo com componentes disponiveis."
}

if ($Install) {
    if (-not (Test-Path ".\ops\install_local_mission.ps1")) {
        throw "ops\install_local_mission.ps1 nao encontrado."
    }

    powershell -ExecutionPolicy Bypass -File ".\ops\install_local_mission.ps1" -Approve -Install
} else {
    Write-Host "Install nao solicitado. Use -Install para instalar missao local."
}

$Request = @{
    mode = "supervised"
    human_approved = $true
    install = [bool]$Install
    auto_execute = $false
    real_execution_enabled = $false
    external_api_enabled = $false
    auto_publish = $false
    auto_send = $false
    auto_deploy = $false
    browser_automation = $false
    mouse_automation = $false
} | ConvertTo-Json -Depth 10 -Compress

& $Python -c "import json; from k_atlas.core.mission_pipeline_runner.runner import MissionPipelineRunner; print(json.dumps(MissionPipelineRunner().run_supervised(json.loads('$Request')), ensure_ascii=False, indent=2))"

if (Test-Path ".\ops\log_cowork_event.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\log_cowork_event.ps1" -Title "Mission Pipeline executado" -Details "Pipeline gerar-converter-instalar executado com Approve=$Approve Install=$Install." -EventType "mission_pipeline"
}

Write-Host "MISSION PIPELINE FINALIZADO."
