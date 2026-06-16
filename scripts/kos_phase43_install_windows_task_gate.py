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
    "phase": "43",
    "module": "K-OS Windows Task Registration Gate",
    "mode": "EXPLICIT_CONFIRMATION_REQUIRED",
    "goal": "permitir registro local do scheduler K-OS no Windows somente com confirmacao humana explicita",
    "task": {
        "name": "KOS-Autonomy-Scheduler-Local",
        "trigger": "AtLogOn",
        "interval_seconds": 900,
        "max_cycles": 0,
        "script": "scripts/start_kos_autonomy_scheduler_manual_loop.ps1",
        "confirmation_required": "YES_REGISTER_KOS_247_LOCAL_ONLY"
    },
    "allowed_actions": {
        "generate_registration_script": True,
        "generate_unregistration_script": True,
        "check_task_status": True,
        "register_task_after_exact_confirmation": True,
        "unregister_task": True
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
import subprocess

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "kos_windows_task_gate_policy.json"
STATUS_PATH = ROOT / "local_runtime" / "kaizen" / "windows_task_status.json"
LOG_DIR = ROOT / "logs" / "kaizen" / "windows_task"

TASK_NAME = "KOS-Autonomy-Scheduler-Local"
CONFIRMATION = "YES_REGISTER_KOS_247_LOCAL_ONLY"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _run(cmd: list[str], timeout: int = 30) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[-4000:],
            "stderr": (proc.stderr or "")[-4000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def check_windows_task_status() -> dict:
    result = _run([
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f"Get-ScheduledTask -TaskName '{TASK_NAME}' -ErrorAction SilentlyContinue | Select-Object TaskName,State | ConvertTo-Json -Compress"
    ])

    installed = bool(result.get("stdout", "").strip())

    status = {
        "status": "WINDOWS_TASK_STATUS_CHECKED",
        "task_name": TASK_NAME,
        "installed": installed,
        "raw": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

    _save_json(STATUS_PATH, status)
    return status

def build_registration_plan() -> dict:
    return {
        "status": "WINDOWS_TASK_REGISTRATION_GATE_READY",
        "task_name": TASK_NAME,
        "confirmation_required": CONFIRMATION,
        "register_script": "scripts/register_kos_autonomy_windows_task.ps1",
        "unregister_script": "scripts/unregister_kos_autonomy_windows_task.ps1",
        "scheduler_script": "scripts/start_kos_autonomy_scheduler_manual_loop.ps1",
        "interval_seconds": 900,
        "max_cycles": 0,
        "registers_without_confirmation": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

if __name__ == "__main__":
    print(json.dumps({
        "plan": build_registration_plan(),
        "task_status": check_windows_task_status()
    }, ensure_ascii=False, indent=2))
'''

register_ps1 = r'''
$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"

$TaskName="KOS-Autonomy-Scheduler-Local"
$Required="YES_REGISTER_KOS_247_LOCAL_ONLY"

Write-Host "[KOS] Registro de tarefa Windows para K-OS 24/7 local."
Write-Host "[KOS] Esta tarefa roda apenas localmente no logon do Windows."
Write-Host "[KOS] Sem Instagram, sem IA paga, sem Codex automatico."
Write-Host "[KOS] Task:" $TaskName

$Confirm=(Read-Host "Para registrar, digite exatamente YES_REGISTER_KOS_247_LOCAL_ONLY").Trim()

if($Confirm -ne $Required){
  Write-Host "[KOS] Confirmacao incorreta. Nenhuma tarefa foi registrada."
  exit 0
}

$ScriptPath=(Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path

$Command = "`$env:KOS_SCHEDULER_INTERVAL_SECONDS='900'; `$env:KOS_SCHEDULER_MAX_CYCLES='0'; & `"$ScriptPath`""

$Action=New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command $Command"
$Trigger=New-ScheduledTaskTrigger -AtLogOn
$Settings=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "K-OS autonomy scheduler local safe loop" -Force | Out-Null

New-Item -ItemType Directory -Force "local_runtime\kaizen" | Out-Null

$Status=[ordered]@{
  status="WINDOWS_TASK_REGISTERED"
  task_name=$TaskName
  script=$ScriptPath
  interval_seconds=900
  max_cycles=0
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\windows_task_status.json" -Encoding UTF8

Write-Host "[KOS] Tarefa registrada com sucesso."
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName,State
'''

unregister_ps1 = r'''
$ErrorActionPreference="Stop"
Set-Location "C:\Users\oi\Desktop\motor-digital"

$TaskName="KOS-Autonomy-Scheduler-Local"

Write-Host "[KOS] Removendo tarefa Windows:" $TaskName

$Task=Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if($Task){
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "[KOS] Tarefa removida."
} else {
  Write-Host "[KOS] Tarefa nao encontrada."
}

New-Item -ItemType Directory -Force "local_runtime\kaizen" | Out-Null

$Status=[ordered]@{
  status="WINDOWS_TASK_UNREGISTERED_OR_NOT_FOUND"
  task_name=$TaskName
  real_action_executed=$false
  paid_ai_call_executed=$false
  instagram_publish_executed=$false
  created_at=(Get-Date).ToString("o")
}

$Status | ConvertTo-Json -Depth 6 | Set-Content "local_runtime\kaizen\windows_task_status.json" -Encoding UTF8
'''

runner_code = r'''
from k_atlas.kaizen.windows_task_gate import build_registration_plan, check_windows_task_status
import json

if __name__ == "__main__":
    print(json.dumps({
        "status": "PHASE43_WINDOWS_TASK_GATE_CHECK_COMPLETED",
        "plan": build_registration_plan(),
        "task_status": check_windows_task_status(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.windows_task_gate import build_registration_plan, check_windows_task_status

st.set_page_config(page_title="KOS Windows Task Gate", layout="wide")

st.title("KOS Windows Task Registration Gate")
st.caption("Registro 24/7 local exige confirmacao explicita no PowerShell.")

plan = build_registration_plan()
status = check_windows_task_status()

col1, col2, col3 = st.columns(3)
col1.metric("Task", plan["task_name"])
col2.metric("Installed", "SIM" if status.get("installed") else "NAO")
col3.metric("Auto paid/publish", "BLOQUEADO")

st.subheader("Plano")
st.json(plan)

st.subheader("Status da tarefa")
st.json(status)

st.subheader("Comandos manuais")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\register_kos_autonomy_windows_task.ps1")
st.code("powershell -ExecutionPolicy Bypass -File scripts\\unregister_kos_autonomy_windows_task.ps1")

st.warning("Esta pagina nao registra tarefa. O registro so acontece pelo script PowerShell com confirmacao exata.")
'''

test_code = r'''
from k_atlas.kaizen.windows_task_gate import build_registration_plan, check_windows_task_status, CONFIRMATION

def test_registration_plan_requires_exact_confirmation():
    plan = build_registration_plan()

    assert plan["status"] == "WINDOWS_TASK_REGISTRATION_GATE_READY"
    assert plan["confirmation_required"] == CONFIRMATION
    assert plan["registers_without_confirmation"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_status_check_is_read_only():
    status = check_windows_task_status()

    assert status["status"] == "WINDOWS_TASK_STATUS_CHECKED"
    assert status["real_action_executed"] is False
    assert status["paid_ai_call_executed"] is False
    assert status["instagram_publish_executed"] is False
'''

save_json(ROOT / "config" / "kos_windows_task_gate_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "windows_task_gate.py", gate_code.strip() + "\n")
write(ROOT / "scripts" / "register_kos_autonomy_windows_task.ps1", register_ps1.strip() + "\n")
write(ROOT / "scripts" / "unregister_kos_autonomy_windows_task.ps1", unregister_ps1.strip() + "\n")
write(ROOT / "scripts" / "run_phase43_windows_task_gate_check.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Windows_Task_Gate.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase43_windows_task_gate.py", test_code.strip() + "\n")

report = {
    "status": "PHASE43_WINDOWS_TASK_GATE_BOOTSTRAPPED",
    "phase": "43",
    "created_files": [
        "config/kos_windows_task_gate_policy.json",
        "k_atlas/kaizen/windows_task_gate.py",
        "scripts/register_kos_autonomy_windows_task.ps1",
        "scripts/unregister_kos_autonomy_windows_task.ps1",
        "scripts/run_phase43_windows_task_gate_check.py",
        "pages/KOS_Windows_Task_Gate.py",
        "tests/test_phase43_windows_task_gate.py"
    ],
    "task_registered_by_bootstrap": False,
    "confirmation_required": "YES_REGISTER_KOS_247_LOCAL_ONLY",
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE43_WINDOWS_TASK_GATE_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))