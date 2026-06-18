from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RUNTIME_PATTERNS = {
    "scheduler_supervisor": "start_kos_autonomy_scheduler_manual_loop.ps1.supervisor.ps1",
    "scheduler_tick": "start_kos_autonomy_scheduler_manual_loop.ps1",
    "local_autonomy_loop": "start_kos_local_autonomy_loop.ps1",
    "engineer_handoff_queue_loop": "start_kos_engineer_handoff_queue_loop.ps1",
    "queue_approval_executor_loop": "start_kos_queue_approval_executor_loop.ps1",
    "autonomous_job_runner_loop": "start_kos_autonomous_job_runner_loop.ps1",
}


def run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        return (completed.stdout or "") + (completed.stderr or "")
    except Exception as exc:
        return str(exc)


def get_git_dirty() -> bool:
    output = run_text(["git", "--no-pager", "status", "--short"])
    return bool(output.strip())


def get_processes() -> list[dict]:
    ps = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.Name -match 'powershell|pwsh|python' } | "
        "Select-Object ProcessId,Name,CommandLine | "
        "ConvertTo-Json -Depth 5"
    )
    raw = run_text([
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        ps,
    ]).strip()

    if not raw:
        return []

    try:
        data = json.loads(raw)
    except Exception:
        return []

    if isinstance(data, dict):
        return [data]

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    return []


def detect_runtime_processes(processes: list[dict]) -> list[dict]:
    detected = []

    for item in processes:
        command_line = str(item.get("CommandLine") or "")
        lowered = command_line.lower()

        for role, pattern in RUNTIME_PATTERNS.items():
            if pattern.lower() in lowered:
                detected.append(
                    {
                        "pid": item.get("ProcessId"),
                        "name": item.get("Name"),
                        "role": role,
                    }
                )
                break

    unique = {}
    for item in detected:
        unique[str(item.get("pid")) + ":" + str(item.get("role"))] = item

    return list(unique.values())


def startup_installed() -> bool:
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        return False

    startup = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    if not startup.exists():
        return False

    try:
        names = [p.name.lower() for p in startup.iterdir()]
    except Exception:
        return False

    return any("kos" in name or "k-os" in name for name in names)


def main() -> int:
    processes = get_processes()
    runtime_processes = detect_runtime_processes(processes)

    git_dirty = get_git_dirty()
    installed = startup_installed()
    background_running = len(runtime_processes) > 0

    health_status = "HEALTHY" if installed and background_running and not git_dirty else "ATTENTION_REQUIRED"

    payload = {
        "status": "PHASE49_RUNTIME_CONTROL_STATUS_COMPLETED",
        "runtime_status": "KOS_RUNTIME_CONTROL_STATUS_READY",
        "startup_installed": installed,
        "background_running": background_running,
        "process_count": len(runtime_processes),
        "health_status": health_status,
        "git_dirty": git_dirty,
        "runtime_processes": runtime_processes,
        "runtime_health_bridge": {
            "enabled": True,
            "recognized_roles": list(RUNTIME_PATTERNS.keys()),
            "note": "Status now recognizes persistent K-OS scheduler supervisor and local autonomy loops.",
        },
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
