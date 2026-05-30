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
from k_atlas.core.mission_pack_bridge.bridge import MissionPackBridge
import json

bridge = MissionPackBridge()
result = bridge.bridge_latest()
print(json.dumps(result, ensure_ascii=False, indent=2))

if result.get("ok"):
    print("LOCAL_MISSION_PATH=" + result.get("output_path", ""))
"@

$Temp = ".mission_pack_bridge_run.py"
Set-Content -Path $Temp -Value $Code -Encoding UTF8
& $Python $Temp
Remove-Item $Temp -Force -ErrorAction SilentlyContinue
