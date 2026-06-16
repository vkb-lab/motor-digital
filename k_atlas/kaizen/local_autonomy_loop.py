from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from k_atlas.kaizen.local_coworker import process_bridge_inbox
from k_atlas.kaizen.local_patch_workspace import create_work_orders_from_coworker_tasks
from k_atlas.kaizen.local_command_composer import create_command_drafts_from_work_orders

ROOT = Path(__file__).resolve().parents[2]
LOOP_DIR = ROOT / "local_runtime" / "kos_local_autonomy_loop"
LOGS_DIR = LOOP_DIR / "logs"
LATEST_STATUS = LOOP_DIR / "latest_loop_status.json"
EVENTS_PATH = LOGS_DIR / "events.jsonl"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def run_local_autonomy_cycle(command_limit: int = 10) -> dict:
    coworker = process_bridge_inbox(limit=command_limit, execute_diagnostics=True)
    workspace = create_work_orders_from_coworker_tasks(limit=command_limit)
    composer = create_command_drafts_from_work_orders(limit=command_limit)

    status = {
        "status": "KOS_LOCAL_AUTONOMY_LOOP_CYCLE_COMPLETED",
        "pipeline": {
            "coworker": {
                "status": coworker.get("status"),
                "commands_seen": coworker.get("commands_seen", 0),
                "created_tasks_count": coworker.get("created_tasks_count", 0),
                "ollama_status": coworker.get("ollama_status", {}).get("status"),
            },
            "patch_workspace": {
                "status": workspace.get("status"),
                "tasks_seen": workspace.get("tasks_seen", 0),
                "created_work_orders_count": workspace.get("created_work_orders_count", 0),
            },
            "command_composer": {
                "status": composer.get("status"),
                "work_orders_seen": composer.get("work_orders_seen", 0),
                "created_command_drafts_count": composer.get("created_command_drafts_count", 0),
            },
        },
        "gates": {
            "execute_generated_commands": False,
            "repo_write_allowed": False,
            "patch_apply_allowed": False,
            "arbitrary_shell_allowed": False,
            "commit_allowed": False,
            "push_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": True,
        },
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_STATUS, status)
    _append_jsonl(EVENTS_PATH, status)
    return status

def get_latest_local_autonomy_loop_status() -> dict:
    if LATEST_STATUS.exists():
        return _read_json(LATEST_STATUS)
    return run_local_autonomy_cycle(command_limit=1)

if __name__ == "__main__":
    print(json.dumps(run_local_autonomy_cycle(), ensure_ascii=False, indent=2))