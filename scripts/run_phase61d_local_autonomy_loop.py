from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.local_autonomy_loop import run_local_autonomy_cycle, get_latest_local_autonomy_loop_status

if __name__ == "__main__":
    result = run_local_autonomy_cycle(command_limit=10)
    latest = get_latest_local_autonomy_loop_status()

    print(json.dumps({
        "status": "PHASE61D_LOCAL_AUTONOMY_LOOP_COMPLETED",
        "result_status": result.get("status"),
        "coworker_created_tasks": result.get("pipeline", {}).get("coworker", {}).get("created_tasks_count"),
        "workspace_created_work_orders": result.get("pipeline", {}).get("patch_workspace", {}).get("created_work_orders_count"),
        "composer_created_command_drafts": result.get("pipeline", {}).get("command_composer", {}).get("created_command_drafts_count"),
        "latest_status": latest.get("status"),
        "execute_generated_commands": False,
        "repo_write_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))