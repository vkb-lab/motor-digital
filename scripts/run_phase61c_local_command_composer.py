from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.local_command_composer import create_command_drafts_from_work_orders, get_latest_command_composer_status

if __name__ == "__main__":
    result = create_command_drafts_from_work_orders(limit=10)
    latest = get_latest_command_composer_status()

    print(json.dumps({
        "status": "PHASE61C_LOCAL_COMMAND_COMPOSER_COMPLETED",
        "result_status": result.get("status"),
        "work_orders_seen": result.get("work_orders_seen"),
        "created_command_drafts_count": result.get("created_command_drafts_count"),
        "latest_status": latest.get("status"),
        "execute_allowed_now": False,
        "repo_write_allowed_now": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))