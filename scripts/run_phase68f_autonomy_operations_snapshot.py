from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REPORTS = {
    "67F_safe_autonomy_baseline": "reports/KOS_PHASE67F_SAFE_AUTONOMY_BASELINE_CERTIFICATION.json",
    "68A_operator_command_inbox": "reports/KOS_PHASE68A_OPERATOR_COMMAND_INBOX_BOOTSTRAP.json",
    "68A1_processed_marker_hotfix": "reports/KOS_PHASE68A1_PROCESSED_MARKER_HOTFIX_CERTIFICATION.json",
    "68B_operator_command_batch": "reports/KOS_PHASE68B_OPERATOR_COMMAND_BATCH_BOOTSTRAP.json",
    "68C_mission_runner": "reports/KOS_PHASE68C_AUTONOMY_MISSION_RUNNER_BOOTSTRAP.json",
    "68D_mission_queue": "reports/KOS_PHASE68D_AUTONOMY_MISSION_QUEUE_BOOTSTRAP.json",
    "68E_mission_queue_loop": "reports/KOS_PHASE68E_AUTONOMY_MISSION_QUEUE_LOOP_BOOTSTRAP.json",
}

RUNTIME_FILES = {
    "kill_switch": "local_runtime/kos_control/AUTONOMY_KILL_SWITCH.json",
    "autonomous_job_runner": "local_runtime/kos_autonomous_jobs/latest_autonomous_job_runner_status.json",
    "autonomous_job_loop_tick": "local_runtime/kos_autonomous_jobs/latest_autonomous_job_runner_loop_tick.json",
    "mission_queue_processor": "local_runtime/kos_autonomy_missions/latest_queue_processor_status.json",
    "mission_queue_loop_tick": "local_runtime/kos_autonomy_missions/latest_mission_queue_loop_tick.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(relpath: str) -> dict[str, Any]:
    path = ROOT / relpath
    if not path.exists():
        return {"exists": False, "path": str(path), "status": "KOS_FILE_NOT_FOUND"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(payload, dict):
            payload["exists"] = True
            payload["path"] = str(path)
            return payload
        return {"exists": True, "path": str(path), "status": "KOS_JSON_NOT_OBJECT"}
    except Exception as exc:
        return {"exists": True, "path": str(path), "status": "KOS_JSON_READ_FAILED", "error": str(exc)}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def build_snapshot() -> dict[str, Any]:
    reports = {name: read_json(path) for name, path in REPORTS.items()}
    runtime_files = {name: read_json(path) for name, path in RUNTIME_FILES.items()}

    missing_reports = [name for name, payload in reports.items() if not payload.get("exists")]
    report_statuses = {name: payload.get("status") for name, payload in reports.items()}

    kill = runtime_files["kill_switch"]
    kill_engaged = bool(kill.get("engaged")) or kill.get("status") == "KOS_AUTONOMY_KILL_SWITCH_ENGAGED"

    return {
        "status": "KOS_AUTONOMY_OPERATIONS_SNAPSHOT_READY" if not missing_reports else "KOS_AUTONOMY_OPERATIONS_SNAPSHOT_ATTENTION_REQUIRED",
        "phase": "68F",
        "report_statuses": report_statuses,
        "missing_reports": missing_reports,
        "runtime_files": runtime_files,
        "kill_switch_engaged": kill_engaged,
        "operator_command": 'powershell -ExecutionPolicy Bypass -File scripts\\submit_kos_operator_command.ps1 -Text "registrar comando operacional" -RunNow',
        "batch_command": 'powershell -ExecutionPolicy Bypass -File scripts\\submit_kos_operator_command_batch.ps1 -Commands @("item 1","item 2") -RunNow',
        "mission_command": 'powershell -ExecutionPolicy Bypass -File scripts\\run_kos_autonomy_mission.ps1 -MissionText "missao" -Objectives @("objetivo 1","objetivo 2") -RunNow',
        "mission_queue_submit_command": 'powershell -ExecutionPolicy Bypass -File scripts\\submit_kos_autonomy_mission_queue.ps1 -MissionText "missao" -Objectives @("objetivo 1","objetivo 2")',
        "mission_queue_process_command": 'powershell -ExecutionPolicy Bypass -File scripts\\process_kos_autonomy_mission_queue.ps1 -Limit 5',
        "kill_switch_engage_command": 'powershell -ExecutionPolicy Bypass -File scripts\\kos_autonomy_kill_switch.ps1 -Action engage -Reason "operator emergency stop"',
        "kill_switch_disengage_command": 'powershell -ExecutionPolicy Bypass -File scripts\\kos_autonomy_kill_switch.ps1 -Action disengage -Reason "operator restore" -RestartRuntime',
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }


def main() -> int:
    snapshot = build_snapshot()
    write_json(ROOT / "local_runtime/kos_autonomy_operations/latest_operations_snapshot.json", snapshot)
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
