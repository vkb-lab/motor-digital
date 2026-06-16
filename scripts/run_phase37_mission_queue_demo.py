from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.mission_queue import create_mission, plan_mission, summarize_queue
import json

if __name__ == "__main__":
    mission = create_mission(
        title="Fase 37 Demo Mission",
        description="Gerar plano seguro para evoluir autonomia do K-OS usando Codex/Ollama em dry-run.",
        priority="high"
    )
    planned = plan_mission(mission["id"])

    print(json.dumps({
        "status": "PHASE37_DEMO_COMPLETED",
        "mission_id": mission["id"],
        "planned_status": planned.get("status"),
        "execution_allowed": False,
        "summary": summarize_queue(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
