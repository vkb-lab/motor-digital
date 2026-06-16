from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "logs" / "kaizen" / "scheduler"
POLICY_PATH = ROOT / "config" / "kos_autonomy_scheduler_policy.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return default

def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def build_scheduler_plan() -> dict:
    policy = _read_json(POLICY_PATH, {})
    scheduler = policy.get("scheduler", {})

    return {
        "status": "SCHEDULER_MANUAL_GATE_READY",
        "mode": policy.get("mode", "MANUAL_LOOP_ONLY"),
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "manual_loop_script": scheduler.get("manual_loop_script", "scripts/start_kos_autonomy_scheduler_manual_loop.ps1"),
        "one_tick_script": scheduler.get("one_tick_script", "scripts/run_phase42_scheduler_once.py"),
        "default_interval_seconds": scheduler.get("default_interval_seconds", 900),
        "default_max_cycles": scheduler.get("default_max_cycles", 1),
        "next_phase_required_for_windows_task": "PHASE_43_EXPLICIT_WINDOWS_TASK_REGISTRATION",
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "created_at": now(),
    }

def run_scheduler_tick(cycle_id: str | None = None) -> dict:
    cycle_id = cycle_id or "scheduler_tick"

    try:
        from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot
        snapshot = build_autonomy_snapshot(write_log=True)
    except Exception as exc:
        snapshot = {
            "status": "SNAPSHOT_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    try:
        from k_atlas.kaizen.safe_executor import run_safe_bundle
        safe_check = run_safe_bundle(
            bundle_id=f"{cycle_id}_dry_run",
            actions=["git_branch", "git_status"],
            dry_run=True,
        )
    except Exception as exc:
        safe_check = {
            "status": "SAFE_EXECUTOR_ERROR",
            "error": str(exc),
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False,
        }

    report = {
        "status": "SCHEDULER_TICK_COMPLETED",
        "cycle_id": cycle_id,
        "mode": "MANUAL_LOOP_ONLY",
        "snapshot": snapshot,
        "safe_check": safe_check,
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now(),
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _save_json(LOG_DIR / "last_tick.json", report)

    return report

def summarize_scheduler() -> dict:
    last_tick = _read_json(LOG_DIR / "last_tick.json", {})
    return {
        "status": "SCHEDULER_SUMMARY",
        "plan": build_scheduler_plan(),
        "last_tick": last_tick,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }

if __name__ == "__main__":
    print(json.dumps(run_scheduler_tick("phase42_smoke"), ensure_ascii=False, indent=2))
