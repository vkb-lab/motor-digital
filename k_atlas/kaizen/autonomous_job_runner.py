from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_ACTIONS = {"write_json_report"}
BLOCKED_ACTIONS = {
    "shell_exec",
    "deploy",
    "paid_ai_call",
    "instagram_publish",
    "browser_logged_account_automation",
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def base_dir(root: Path | None = None) -> Path:
    root = root or ROOT
    return root / "local_runtime" / "kos_autonomous_jobs"

def inbox_dir(root: Path | None = None) -> Path:
    return base_dir(root) / "inbox"

def processed_dir(root: Path | None = None) -> Path:
    return base_dir(root) / "processed"

def failed_dir(root: Path | None = None) -> Path:
    return base_dir(root) / "failed"

def output_dir(root: Path | None = None) -> Path:
    return base_dir(root) / "output"

def ensure_dirs(root: Path | None = None) -> None:
    for path in [inbox_dir(root), processed_dir(root), failed_dir(root), output_dir(root)]:
        path.mkdir(parents=True, exist_ok=True)

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def kill_switch_engaged(root: Path | None = None) -> bool:
    root = root or ROOT
    path = root / "local_runtime" / "kos_control" / "AUTONOMY_KILL_SWITCH.json"

    if not path.exists():
        return False

    try:
        payload = read_json(path)
    except Exception:
        return True

    status = str(payload.get("status") or "").strip()

    if status == "KOS_AUTONOMY_KILL_SWITCH_ENGAGED":
        return True

    if status == "KOS_AUTONOMY_KILL_SWITCH_DISENGAGED":
        return False

    if payload.get("engaged") is True:
        return True

    return False

def safe_output_path(relpath: str, root: Path | None = None) -> Path:
    root = root or ROOT
    allowed_base = output_dir(root).resolve()
    candidate = (root / relpath).resolve()
    if not str(candidate).startswith(str(allowed_base)):
        raise ValueError("output path fora da area permitida")
    return candidate

def fail_job(job_path: Path, reason: str, root: Path | None = None) -> dict[str, Any]:
    ensure_dirs(root)
    payload = {
        "status": "KOS_AUTONOMOUS_JOB_FAILED",
        "job_path": str(job_path),
        "reason": reason,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }
    marker = failed_dir(root) / (job_path.stem + "_failed.json")
    write_json(marker, payload)
    if job_path.exists():
        shutil.move(str(job_path), str(failed_dir(root) / job_path.name))
    return payload

def process_job(job_path: Path, root: Path | None = None) -> dict[str, Any]:
    ensure_dirs(root)

    if job_path.name.endswith(".tmp.json"):
        return {
            "status": "KOS_AUTONOMOUS_JOB_IGNORED_TMP",
            "job_path": str(job_path),
            "created_at": now_iso(),
        }

    if kill_switch_engaged(root):
        return fail_job(job_path, "blocked_by_kill_switch", root)

    try:
        job = read_json(job_path)
    except Exception as exc:
        return fail_job(job_path, "invalid_json: " + str(exc), root)

    job_id = str(job.get("job_id") or job_path.stem)
    action = str(job.get("action") or "")

    if action in BLOCKED_ACTIONS:
        return fail_job(job_path, "blocked_action: " + action, root)

    if action not in ALLOWED_ACTIONS:
        return fail_job(job_path, "action_not_allowed: " + action, root)

    if action == "write_json_report":
        relpath = str(job.get("output_relpath") or f"local_runtime/kos_autonomous_jobs/output/{job_id}.json")
        payload = job.get("payload") or {}
        output_path = safe_output_path(relpath, root)
        output_payload = {
            "status": "KOS_AUTONOMOUS_JOB_OUTPUT_CREATED",
            "job_id": job_id,
            "action": action,
            "payload": payload,
            "real_action_executed": True,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "created_at": now_iso(),
        }
        write_json(output_path, output_payload)

        result = {
            "status": "KOS_AUTONOMOUS_JOB_EXECUTED",
            "job_id": job_id,
            "action": action,
            "output_path": str(output_path),
            "returncode": 0,
            "real_action_executed": True,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
            "browser_logged_account_automation_used": False,
            "created_at": now_iso(),
        }
        result_path = processed_dir(root) / (job_id + ".json")
        write_json(result_path, result)

        archived_job_path = processed_dir(root) / (job_id + "_source.json")
        if job_path.exists():
            if archived_job_path.exists():
                archived_job_path.unlink()
            shutil.move(str(job_path), str(archived_job_path))

        return result

    return fail_job(job_path, "unhandled_action", root)

def process_inbox(limit: int = 5, root: Path | None = None) -> dict[str, Any]:
    ensure_dirs(root)
    jobs = sorted(
        [p for p in inbox_dir(root).glob("*.json") if not p.name.endswith(".tmp.json")],
        key=lambda p: p.stat().st_mtime,
    )[:limit]

    processed = [process_job(path, root) for path in jobs]

    status = {
        "status": "KOS_AUTONOMOUS_JOB_RUNNER_STATUS",
        "pending_count": len(list(inbox_dir(root).glob("*.json"))),
        "processed_count": len(processed),
        "processed": processed,
        "kill_switch_engaged": kill_switch_engaged(root),
        "real_action_executed": any(item.get("real_action_executed") for item in processed),
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }
    write_json(base_dir(root) / "latest_autonomous_job_runner_status.json", status)
    return status


