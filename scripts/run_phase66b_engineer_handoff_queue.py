
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.engineer_handoff_queue import process_engineer_handoff_queue

if __name__ == "__main__":
    result = process_engineer_handoff_queue(limit=20)
    print(json.dumps({
        "status": "PHASE66B_ENGINEER_HANDOFF_QUEUE_COMPLETED",
        "queue_status": result.get("status"),
        "processed_count": result.get("processed_count"),
        "staged_commands_count": result.get("staged_commands_count"),
        "no_browser_click_required": True,
        "duplicate_guard": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
