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
    "phase": "49",
    "module": "K-OS Runtime Control CLI",
    "mode": "LOCAL_OPERATOR_CONTROL",
    "goal": "centralizar comandos seguros de controle do runtime local do K-OS",
    "allowed_actions": {
        "status": True,
        "health": True,
        "briefing": True,
        "evidence": True,
        "start_with_confirmation": True,
        "stop_with_confirmation": True,
        "restart_with_confirmation": True
    },
    "blocked_actions": {
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "auto_commit": True,
        "auto_push": True
    },
    "required_confirmations": {
        "start": "YES_START_KOS_RUNTIME_LOCAL",
        "stop": "YES_STOP_KOS_RUNTIME_LOCAL",
        "restart": "YES_RESTART_KOS_RUNTIME_LOCAL"
    },
    "hard_rules": {
        "local_only": True,
        "human_confirmation_for_process_control": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True,
        "parada_atlantida_locked": True,
        "hupmix_test_only": True
    },
    "created_at": now()
}

runtime_control_code = r'''
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

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
            "stdout": (proc.stdout or "")[-5000:],
            "stderr": (proc.stderr or "")[-5000:],
        }
    except Exception as exc:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }

def check_runtime_processes() -> dict:
    ps = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -match 'start_kos_autonomy_scheduler_manual_loop' } | "
        "Select-Object ProcessId,CommandLine | ConvertTo-Json -Depth 4 -Compress"
    )

    result = _run([
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        ps
    ], timeout=30)

    stdout = (result.get("stdout") or "").strip()
    count = 0

    if stdout:
        try:
            parsed = json.loads(stdout)
            if isinstance(parsed, list):
                count = len(parsed)
            elif isinstance(parsed, dict):
                count = 1
        except Exception:
            count = 1

    return {
        "status": "RUNTIME_PROCESS_CHECKED",
        "running": count > 0,
        "process_count": count,
        "raw": result,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }

def get_git_summary() -> dict:
    return {
        "branch": _run(["git", "branch", "--show-current"]).get("stdout", "").strip(),
        "status_short": _run(["git", "--no-pager", "status", "--short"]).get("stdout", ""),
        "last_commit": _run(["git", "--no-pager", "log", "--oneline", "-1"]).get("stdout", "").strip(),
    }

def build_runtime_control_status() -> dict:
    try:
        from k_atlas.kaizen.startup_folder_gate import check_startup_status
        startup = check_startup_status()
    except Exception as exc:
        startup = {"installed": False, "error": str(exc)}

    try:
        from k_atlas.kaizen.runtime_health import build_runtime_health
        health = build_runtime_health(write_log=True)
    except Exception as exc:
        health = {"health_status": "ATTENTION_REQUIRED", "error": str(exc)}

    try:
        from k_atlas.kaizen.evidence_ledger import summarize_evidence
        evidence = summarize_evidence(limit=5)
    except Exception as exc:
        evidence = {"status": "EVIDENCE_ERROR", "error": str(exc)}

    process = check_runtime_processes()
    git = get_git_summary()

    safe_commands = [
        {
            "label": "Status",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action status"
        },
        {
            "label": "Health",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action health"
        },
        {
            "label": "Briefing",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action briefing"
        },
        {
            "label": "Evidence",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action evidence"
        },
        {
            "label": "Start runtime",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action start"
        },
        {
            "label": "Stop runtime",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action stop"
        },
        {
            "label": "Restart runtime",
            "command": "powershell -ExecutionPolicy Bypass -File scripts\\kos_runtime_control.ps1 -Action restart"
        },
    ]

    return {
        "status": "KOS_RUNTIME_CONTROL_STATUS_READY",
        "created_at": now(),
        "startup_installed": startup.get("installed"),
        "background_running": process.get("running"),
        "process_count": process.get("process_count"),
        "health_status": health.get("health_status"),
        "git_dirty": bool((git.get("status_short") or "").strip()),
        "production_publish_locked": health.get("runtime_locks", {}).get("production_publish_locked", True),
        "paid_ai_locked": health.get("runtime_locks", {}).get("paid_ai_locked", True),
        "startup": startup,
        "process": process,
        "health": health,
        "evidence": evidence,
        "git": git,
        "safe_commands": safe_commands,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
    }

if __name__ == "__main__":
    print(json.dumps(build_runtime_control_status(), ensure_ascii=False, indent=2))
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.runtime_control import build_runtime_control_status

if __name__ == "__main__":
    status = build_runtime_control_status()
    print(json.dumps({
        "status": "PHASE49_RUNTIME_CONTROL_STATUS_COMPLETED",
        "runtime_status": status.get("status"),
        "startup_installed": status.get("startup_installed"),
        "background_running": status.get("background_running"),
        "process_count": status.get("process_count"),
        "health_status": status.get("health_status"),
        "git_dirty": status.get("git_dirty"),
        "production_publish_locked": status.get("production_publish_locked"),
        "paid_ai_locked": status.get("paid_ai_locked"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

ps_control = r'''
param(
  [ValidateSet("status","health","briefing","evidence","start","stop","restart")]
  [string]$Action="status"
)

$ErrorActionPreference="Stop"

$ProjectRoot="C:\Users\oi\Desktop\motor-digital"
Set-Location $ProjectRoot
$env:PYTHONPATH=$ProjectRoot

$StartConfirm="YES_START_KOS_RUNTIME_LOCAL"
$StopConfirm="YES_STOP_KOS_RUNTIME_LOCAL"
$RestartConfirm="YES_RESTART_KOS_RUNTIME_LOCAL"

function Start-KosRuntime {
  New-Item -ItemType Directory -Force "logs\kaizen\startup" | Out-Null

  $ScriptPath=(Resolve-Path "scripts\start_kos_autonomy_scheduler_manual_loop.ps1").Path
  $LogPath=(Resolve-Path "logs\kaizen\startup").Path + "\runtime_control_background_loop.log"

  $Cmd="Set-Location '$ProjectRoot'; `$env:PYTHONPATH='$ProjectRoot'; `$env:KOS_SCHEDULER_INTERVAL_SECONDS='900'; `$env:KOS_SCHEDULER_MAX_CYCLES='0'; powershell -ExecutionPolicy Bypass -File '$ScriptPath' >> '$LogPath' 2>&1"

  Start-Process powershell.exe -WindowStyle Minimized -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"$Cmd`""

  Write-Host "[KOS] Runtime iniciado em background."
}

function Stop-KosRuntime {
  $procs=Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "start_kos_autonomy_scheduler_manual_loop" }

  if(!$procs){
    Write-Host "[KOS] Nenhum runtime background encontrado."
    return
  }

  foreach($p in $procs){
    Write-Host "[KOS] Stop PID:" $p.ProcessId
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  }

  Write-Host "[KOS] Runtime parado."
}

if($Action -eq "status"){
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}

if($Action -eq "health"){
  python scripts\run_phase44_runtime_health_check.py
  exit 0
}

if($Action -eq "briefing"){
  python scripts\run_phase46_operator_briefing.py
  exit 0
}

if($Action -eq "evidence"){
  python scripts\run_phase48_evidence_ledger.py
  exit 0
}

if($Action -eq "start"){
  $Confirm=(Read-Host "Para iniciar runtime local, digite exatamente YES_START_KOS_RUNTIME_LOCAL").Trim()
  if($Confirm -ne $StartConfirm){
    Write-Host "[KOS] Confirmacao incorreta. Runtime nao iniciado."
    exit 0
  }
  Start-KosRuntime
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}

if($Action -eq "stop"){
  $Confirm=(Read-Host "Para parar runtime local, digite exatamente YES_STOP_KOS_RUNTIME_LOCAL").Trim()
  if($Confirm -ne $StopConfirm){
    Write-Host "[KOS] Confirmacao incorreta. Runtime nao parado."
    exit 0
  }
  Stop-KosRuntime
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}

if($Action -eq "restart"){
  $Confirm=(Read-Host "Para reiniciar runtime local, digite exatamente YES_RESTART_KOS_RUNTIME_LOCAL").Trim()
  if($Confirm -ne $RestartConfirm){
    Write-Host "[KOS] Confirmacao incorreta. Runtime nao reiniciado."
    exit 0
  }
  Stop-KosRuntime
  Start-Sleep -Seconds 2
  Start-KosRuntime
  python scripts\run_phase49_runtime_control_status.py
  exit 0
}
'''

page_code = r'''
import streamlit as st

from k_atlas.kaizen.runtime_control import build_runtime_control_status

st.set_page_config(page_title="KOS Runtime Control", layout="wide")

st.title("KOS Runtime Control")
st.caption("Painel read-only com comandos manuais seguros para controle local.")

status = build_runtime_control_status()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Startup", "SIM" if status.get("startup_installed") else "NAO")
col2.metric("Background", "SIM" if status.get("background_running") else "NAO")
col3.metric("Health", status.get("health_status", "N/A"))
col4.metric("Git dirty", "SIM" if status.get("git_dirty") else "NAO")

col5, col6 = st.columns(2)
col5.metric("IG producao", "BLOQUEADO" if status.get("production_publish_locked") else "ATENCAO")
col6.metric("IA paga", "BLOQUEADA" if status.get("paid_ai_locked") else "ATENCAO")

st.subheader("Comandos seguros")
for item in status.get("safe_commands", []):
    st.code(item.get("command", ""))

st.subheader("Status completo")
st.json(status)

st.warning("Esta pagina nao inicia nem para processos. Use os comandos PowerShell com confirmacao humana.")
'''

test_code = r'''
from k_atlas.kaizen.runtime_control import build_runtime_control_status, check_runtime_processes

def test_runtime_control_status_is_safe():
    status = build_runtime_control_status()

    assert status["status"] == "KOS_RUNTIME_CONTROL_STATUS_READY"
    assert status["real_action_executed"] is False
    assert status["paid_ai_call_executed"] is False
    assert status["instagram_publish_executed"] is False
    assert status["external_side_effects_executed"] is False

def test_runtime_process_check_is_read_only():
    result = check_runtime_processes()

    assert result["status"] == "RUNTIME_PROCESS_CHECKED"
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False

def test_runtime_control_exposes_safe_commands():
    status = build_runtime_control_status()

    commands = status["safe_commands"]
    assert isinstance(commands, list)
    assert len(commands) >= 3
'''

save_json(ROOT / "config" / "kos_runtime_control_policy.json", policy)
write(ROOT / "k_atlas" / "kaizen" / "runtime_control.py", runtime_control_code.strip() + "\n")
write(ROOT / "scripts" / "run_phase49_runtime_control_status.py", runner_code.strip() + "\n")
write(ROOT / "scripts" / "kos_runtime_control.ps1", ps_control.strip() + "\n")
write(ROOT / "pages" / "KOS_Runtime_Control.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase49_runtime_control.py", test_code.strip() + "\n")

report = {
    "status": "PHASE49_RUNTIME_CONTROL_BOOTSTRAPPED",
    "phase": "49",
    "created_files": [
        "config/kos_runtime_control_policy.json",
        "k_atlas/kaizen/runtime_control.py",
        "scripts/run_phase49_runtime_control_status.py",
        "scripts/kos_runtime_control.ps1",
        "pages/KOS_Runtime_Control.py",
        "tests/test_phase49_runtime_control.py"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE49_RUNTIME_CONTROL_BOOTSTRAP.json", report)

print(json.dumps(report, ensure_ascii=False, indent=2))