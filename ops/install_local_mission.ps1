param(
    [string]$MissionPath = "",
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

$Code = @"
from k_atlas.core.local_mission_installer.installer import LocalMissionInstaller
import json

installer = LocalMissionInstaller()

mission_path = r"$MissionPath"
approve = "$Approve" == "True"
install = "$Install" == "True"

if mission_path:
    result = installer.import_mission_file(mission_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))

dry = installer.dry_run()
print(json.dumps(dry, ensure_ascii=False, indent=2))

if approve:
    approval = installer.approve_mission()
    print(json.dumps(approval, ensure_ascii=False, indent=2))

if install:
    installed = installer.install_manual({
        "human_approved": True,
        "install_mode": "manual",
        "auto_execute": False,
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "browser_automation": False,
        "mouse_automation": False,
    })
    print(json.dumps(installed, ensure_ascii=False, indent=2))
"@

$Temp = ".local_mission_installer_run.py"
Set-Content -Path $Temp -Value $Code -Encoding UTF8
& $Python $Temp
Remove-Item $Temp -Force -ErrorAction SilentlyContinue
