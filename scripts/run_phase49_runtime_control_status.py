from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.runtime_control import build_runtime_control_status

if __name__ == "__main__":
    status = build_runtime_control_status()
    print(json.dumps({
        "status": "PHASE49_RUNTIME_CONTROL_STATUS_COMPLETED",
        "runtime_status": status.get("status"),
        "startup_installed": status.get("startup_installed"),
        "background_running": status.get("background_running"),
        "process_count": status.get("process_count"),
        "health_status": status.get("health_status"),
        "git_dirty": status.get("git_dirty"),
        "production_publish_locked": status.get("production_publish_locked"),
        "paid_ai_locked": status.get("paid_ai_locked"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
