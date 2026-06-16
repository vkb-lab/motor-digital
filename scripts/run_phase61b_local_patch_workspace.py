from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.local_patch_workspace import create_work_orders_from_coworker_tasks, get_latest_patch_workspace_status

if __name__ == "__main__":
    result = create_work_orders_from_coworker_tasks(limit=10)
    latest = get_latest_patch_workspace_status()

    print(json.dumps({
        "status": "PHASE61B_LOCAL_PATCH_WORKSPACE_COMPLETED",
        "result_status": result.get("status"),
        "tasks_seen": result.get("tasks_seen"),
        "created_work_orders_count": result.get("created_work_orders_count"),
        "latest_status": latest.get("status"),
        "repo_write_allowed_now": False,
        "patch_apply_allowed_now": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))