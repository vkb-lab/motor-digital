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
