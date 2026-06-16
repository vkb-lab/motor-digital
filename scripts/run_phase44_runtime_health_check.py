from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.runtime_health import build_runtime_health

if __name__ == "__main__":
    result = build_runtime_health(write_log=True)
    print(json.dumps({
        "status": "PHASE44_RUNTIME_HEALTH_CHECK_COMPLETED",
        "health_status": result.get("health_status"),
        "warnings": result.get("warnings", []),
        "startup_installed": result.get("startup_folder", {}).get("installed"),
        "background_running": result.get("background_processes", {}).get("running"),
        "scheduler_tick_exists": result.get("scheduler_last_tick", {}).get("exists"),
        "git_dirty": bool(result.get("git", {}).get("status_short", "").strip()),
        "production_publish_locked": result.get("runtime_locks", {}).get("production_publish_locked"),
        "paid_ai_locked": result.get("runtime_locks", {}).get("paid_ai_locked"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
