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
    throw "Python virtualenv nao encontrado."
}

$env:PYTHONPATH = (Get-Location).Path
$env:PYTHONIOENCODING = "utf-8"

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Value
    )
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) $Path), $Value, $Encoding)
}

Write-Host "K-Atlas Mission Pipeline Runner"
Write-Host "Fluxo: 74 gerar -> 75 converter -> 73 instalar"
Write-Host ""

if (-not $Approve) {
    Write-Host "Dry-run apenas. Para instalar, use: -Approve -Install"
    & $Python -m k_atlas.core.mission_pipeline_runner.run_demo
    exit 0
}

Write-Host "Aprovacao humana detectada."

if (Test-Path ".\ops\generate_local_mission_pack.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\generate_local_mission_pack.ps1"
} elseif (Test-Path ".\ops\run_mission_pack_generator_demo.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\run_mission_pack_generator_demo.ps1"
} else {
    throw "Nenhum script de geracao de mission pack encontrado."
}

if (Test-Path ".\ops\bridge_latest_mission_pack.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\bridge_latest_mission_pack.ps1"
} elseif (Test-Path ".\ops\run_mission_pack_bridge_demo.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\run_mission_pack_bridge_demo.ps1"
} else {
    throw "Nenhum script de bridge encontrado."
}

$MissionPath = "live\mission_pack_bridge\latest_local_mission.kmission.json"

if (-not (Test-Path $MissionPath)) {
    $LatestMission = Get-ChildItem "live\mission_pack_bridge" -Filter "*.kmission.json" -File -Recurse -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($LatestMission) {
        $MissionPath = $LatestMission.FullName
    }
}

if ($Install) {
    if (-not (Test-Path ".\ops\install_local_mission.ps1")) {
        throw "ops\install_local_mission.ps1 nao encontrado."
    }

    if (-not (Test-Path $MissionPath)) {
        throw "Missao local convertida nao encontrada."
    }

    powershell -ExecutionPolicy Bypass -File ".\ops\install_local_mission.ps1" -MissionPath $MissionPath -Approve -Install
} else {
    Write-Host "Install nao solicitado. Use -Install para instalar missao local."
}

$Request = [ordered]@{
    mode = "supervised"
    human_approved = [bool]$Approve
    install = [bool]$Install
    auto_execute = $false
    real_execution_enabled = $false
    external_api_enabled = $false
    auto_publish = $false
    auto_send = $false
    auto_deploy = $false
    browser_automation = $false
    mouse_automation = $false
}

$RequestJson = $Request | ConvertTo-Json -Depth 20
Write-Utf8NoBom -Path ".mission_pipeline_request.json" -Value $RequestJson

$PythonCode = @"
import json
from pathlib import Path
from k_atlas.core.mission_pipeline_runner.runner import MissionPipelineRunner

request = json.loads(Path(".mission_pipeline_request.json").read_text(encoding="utf-8-sig"))
result = MissionPipelineRunner().run_supervised(request)

payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
Path(".mission_pipeline_result.json").write_text(payload, encoding="utf-8")
print(payload)

if result.get("ok") is not True:
    raise SystemExit(2)
"@

Write-Utf8NoBom -Path ".mission_pipeline_execute.py" -Value $PythonCode

& $Python ".mission_pipeline_execute.py"

if ($LASTEXITCODE -ne 0) {
    throw "Mission Pipeline Runner retornou erro."
}

Remove-Item ".mission_pipeline_request.json" -Force -ErrorAction SilentlyContinue
Remove-Item ".mission_pipeline_execute.py" -Force -ErrorAction SilentlyContinue
Remove-Item ".mission_pipeline_result.json" -Force -ErrorAction SilentlyContinue

if (Test-Path ".\ops\log_cowork_event.ps1") {
    powershell -ExecutionPolicy Bypass -File ".\ops\log_cowork_event.ps1" -Title "Pipeline 76 corrigido" -Details "Pipeline 74-75-73 executado com gerador correto, bridge e instalador local aprovado." -EventType "pipeline_fix"
}

Write-Host "MISSION PIPELINE OK"