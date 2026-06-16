from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.briefing_scheduler import run_briefing_scheduler_tick, summarize_briefing_scheduler

if __name__ == "__main__":
    result = run_briefing_scheduler_tick("phase47_manual_tick")
    print(json.dumps({
        "status": "PHASE47_BRIEFING_SCHEDULER_TICK_COMPLETED",
        "tick_status": result.get("status"),
        "briefing_status": result.get("operator_briefing", {}).get("status"),
        "risk_level": result.get("operator_briefing", {}).get("risk_level"),
        "summary": summarize_briefing_scheduler(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
