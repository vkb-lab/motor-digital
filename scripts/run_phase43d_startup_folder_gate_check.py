from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.startup_folder_gate import build_startup_plan, check_startup_status
import json

if __name__ == "__main__":
    print(json.dumps({
        "status": "PHASE43D_STARTUP_FOLDER_GATE_CHECK_COMPLETED",
        "plan": build_startup_plan(),
        "startup_status": check_startup_status(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
