
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.engineer_handoff_bridge import get_engineer_handoff_status

if __name__ == "__main__":
    result = get_engineer_handoff_status()
    print(json.dumps({
        "status": "PHASE66_ENGINEER_HANDOFF_BRIDGE_COMPLETED",
        "bridge_status": result.get("status"),
        "staged_commands_count": result.get("staged_commands_count"),
        "confirmation_required": result.get("confirmation_required"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
