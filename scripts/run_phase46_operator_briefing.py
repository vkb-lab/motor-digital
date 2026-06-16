from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.operator_briefing import build_operator_briefing

if __name__ == "__main__":
    result = build_operator_briefing(write_log=True)
    print(json.dumps({
        "status": "PHASE46_OPERATOR_DAILY_BRIEFING_COMPLETED",
        "briefing_status": result.get("status"),
        "risk_level": result.get("risk_level"),
        "health_status": result.get("health_status"),
        "priorities": result.get("priorities", []),
        "warnings_count": len(result.get("warnings", [])),
        "issues_count": len(result.get("issues", [])),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
