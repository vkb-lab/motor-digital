from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.scheduler_gate import run_scheduler_tick, build_scheduler_plan
import json

if __name__ == "__main__":
    result = run_scheduler_tick("phase42_manual_tick")

    print(json.dumps({
        "status": "PHASE42_SCHEDULER_TICK_COMPLETED",
        "tick_status": result.get("status"),
        "scheduler_plan": build_scheduler_plan(),
        "windows_task_registered": False,
        "auto_start_enabled": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
