from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

policy = {
    "status": "ACTIVE",
    "phase": "43D",
    "module": "K-OS Startup Folder Gate",
    "mode": "USER_STARTUP_FALLBACK_EXPLICIT_CONFIRMATION",
    "goal": "ativar loop local do K-OS no login do usuario sem exigir admin, usando Startup Folder",
    "confirmation_required": "YES_REGISTER_KOS_STARTUP_LOCAL_ONLY",
    "startup_entry": "KOS-Autonomy-Scheduler-Local.cmd",
    "allowed_actions": {
        "check_startup_entry": True,
        "register_after_exact_confirmation": True,
        "unregister_startup_entry": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_access": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "register_without_exact_confirmation": True
    },
    "hard_rules": {
        "no_admin_required": True,
        "exact_confirmation_required": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

gate_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = ROOT / "local_runtime" / "kaizen" / "startup_folder_status.json"

ENTRY_NAME = "KOS-Autonomy-Scheduler-Local.cmd"
CONFIRMATION = "YES_REGISTER_KOS_STARTUP_LOCAL_ONLY"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def startup_folder() -> Path:
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

def startup_entry_path() -> Path:
    return startup_folder() / ENTRY_NAME

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def check_startup_status() -> dict:
    folder = startup_folder()
    entry = startup_entry_path()

    status = {
        "status": "STARTUP_FOLDER_STATUS_CHECKED",
        "startup_folder": str(folder),
        "entry_name": ENTRY_NAME,
        "entry_path": str(entry),
        "installed": entry.exists(),
        "confirmation_required": CONFIRMATION,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

    _save_json(STATUS_PATH, status)
    return status

def build_startup_plan() -> dict:
    return {
        "status": "STARTUP_FOLDER_GATE_READY",
        "entry_name": ENTRY_NAME,
        "confirmation_required": CONFIRMATION,
        "register_script": "scripts/register_kos_autonomy_startup_folder.ps1",
        "unregister_script": "scripts/unregister_kos_autonomy_startup_folder.ps1",
        "requires_admin": False,
        "registers_without_confirmation": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

if __name__ == "__main__":
    print(json.dumps({
        "plan": build_startup_plan(),
        "startup_status": check_startup_status()
    }, ensure_ascii=False, indent=2))
'''

register_ps1 = r'''
$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot

$Required="YES_REGISTER_KOS_STARTUP_LOCAL_ONLY"
$EntryName="KOS-Autonomy-Scheduler-Local.cmd"
$StartupFolder=[Environment]::GetFolderPath("Startup")
$EntryPath=Join-Path $StartupFolder $EntryName

Write-Host "[KOS] Registro via Startup Folder do usuario."
Write-Host "[KOS] Nao requer admin."
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."
Write-Host "[KOS] Startup folder:" $StartupFolder
Write-Host "[KOS] Entry:" $EntryPath

$Confirm=(Read-Host "Para registrar, digite exatamente YES_REGISTER_KOS_STARTUP_LOCAL_ONLY").Trim()

if($Confirm -ne $Required){
  Write-Host "[KOS] Confirmacao incorreta. Nenhum startup foi registrado."
  exit 0
}

New-Item -ItemType Directory -Force $StartupFolder | Out-Null
New-Item -ItemType Directory -Force "logs\kaizen\startup","local_runtime\kaizen" | Out-Null

$SchedulerScript=(Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path
$LogPath=(Resolve-Path "logs\kaizen\startup").Path + "\startup_loop.log"

$Cmd = @"
@echo off
cd /d "$ProjectRoot"
set PYTHONPATH=$ProjectRoot
set KOS_SCHEDULER_INTERVAL_SECONDS=900
set KOS_SCHEDULER_MAX_CYCLES=0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$SchedulerScript" >> "$LogPath" 2>&1
"@

[System.IO.File]::WriteAllText($EntryPath, $Cmd, [System.Text.UTF8Encoding]::new($false))

$Status=[ordered]@{
  status="STARTUP_FOLDER_ENTRY_REGISTERED"
  entry_path=$EntryPath
  startup_folder=$StartupFolder
  requires_admin=$false
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\startup_folder_status.json" -Encoding UTF8

Write-Host "[KOS] Startup Folder registrado com sucesso."
Write-Host "[KOS] O K-OS iniciara no proximo login do Windows."
Write-Host "[KOS] Para iniciar agora manualmente, rode:"
Write-Host "powershell -ExecutionPolicy Bypass -File scripts\start_kos_autonomy_scheduler_manual_loop.ps1"
'''

unregister_ps1 = r'''
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
'''

runner_code = r'''
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.startup_folder_gate import build_startup_plan, check_startup_status
import json

if __name__ == "__main__":
    print(json.dumps({
        "status": "PHASE43D_STARTUP_FOLDER_GATE_CHECK_COMPLETED",
        "plan": build_startup_plan(),
        "startup_status": check_startup_status(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.startup_folder_gate import build_startup_plan, check_startup_status

st.set_page_config(page_title="KOS Startup Folder Gate", layout="wide")

st.title("KOS Startup Folder Gate")
st.caption("Fallback sem admin para iniciar K-OS no login do usuario.")

plan = build_startup_plan()
status = check_startup_status()

col1, col2, col3 = st.columns(3)
col1.metric("Entry", plan["entry_name"])
col2.metric("Installed", "SIM" if status.get("installed") else "NAO")
col3.metric("Requires admin", "NAO")

st.subheader("Plano")
st.json(plan)

st.subheader("Status")
st.json(status)

st.subheader("Comandos")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\register_kos_autonomy_startup_folder.ps1")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\unregister_kos_autonomy_startup_folder.ps1")

st.warning("Esta pagina nao registra nada. O registro exige PowerShell e confirmacao exata.")
'''

test_code = r'''
from k_atlas.kaizen.startup_folder_gate import build_startup_plan, check_startup_status, CONFIRMATION

def test_startup_plan_requires_confirmation():
    plan = build_startup_plan()

    assert plan["status"] == "STARTUP_FOLDER_GATE_READY"
    assert plan["confirmation_required"] == CONFIRMATION
    assert plan["requires_admin"] is False
    assert plan["registers_without_confirmation"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_startup_status_check_is_read_only():
    status = check_startup_status()

    assert status["status"] == "STARTUP_FOLDER_STATUS_CHECKED"
    assert status["real_action_executed"] is False
    assert status["paid_ai_call_executed"] is False
    assert status["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_startup_folder_gate_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "startup_folder_gate.py", gate_code.strip() + "\n")
write(ROOT / "scripts" / "register_kos_autonomy_startup_folder.ps1", register_ps1.strip() + "\n")
write(ROOT / "scripts" / "unregister_kos_autonomy_startup_folder.ps1", unregister_ps1.strip() + "\n")
write(ROOT / "scripts" / "run_phase43d_startup_folder_gate_check.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Startup_Folder_Gate.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase43d_startup_folder_gate.py", test_code.strip() + "\n")

report = {
    "status": "PHASE43D_STARTUP_FOLDER_GATE_BOOTSTRAPPED",
    "phase": "43D",
    "created_files": [
        "config/kos_startup_folder_gate_policy.json",
        "k_atlas/kaizen/startup_folder_gate.py",
        "scripts/register_kos_autonomy_startup_folder.ps1",
        "scripts/unregister_kos_autonomy_startup_folder.ps1",
        "scripts/run_phase43d_startup_folder_gate_check.py",
        "pages/KOS_Startup_Folder_Gate.py",
        "tests/test_phase43d_startup_folder_gate.py"
    ],
    "startup_registered_by_bootstrap": False,
    "confirmation_required": "YES_REGISTER_KOS_STARTUP_LOCAL_ONLY",
    "requires_admin": False,
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE43D_STARTUP_FOLDER_GATE_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))