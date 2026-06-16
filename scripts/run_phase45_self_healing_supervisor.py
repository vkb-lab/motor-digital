from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.self_healing_supervisor import run_self_healing_supervisor

if __name__ == "__main__":
    result = run_self_healing_supervisor(write_log=True)
    plan = result.get("recovery_plan", {})

    print(json.dumps({
        "status": "PHASE45_SELF_HEALING_SUPERVISOR_COMPLETED",
        "supervisor_status": result.get("status"),
        "issues_count": len(plan.get("issues", [])),
        "warnings": plan.get("warnings", []),
        "manual_commands_count": len(plan.get("manual_recovery_commands", [])),
        "auto_repair_executed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
