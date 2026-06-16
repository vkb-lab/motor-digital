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
