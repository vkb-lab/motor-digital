from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.local_coworker import process_bridge_inbox, get_latest_status

if __name__ == "__main__":
    result = process_bridge_inbox(limit=5, execute_diagnostics=True)
    latest = get_latest_status()

    print(json.dumps({
        "status": "PHASE61A_LOCAL_COWORKER_TICK_COMPLETED",
        "result_status": result.get("status"),
        "commands_seen": result.get("commands_seen"),
        "created_tasks_count": result.get("created_tasks_count"),
        "ollama_status": result.get("ollama_status", {}).get("status"),
        "latest_status": latest.get("status"),
        "repo_write_allowed": False,
        "arbitrary_shell_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))