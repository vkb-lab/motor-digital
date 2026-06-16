from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import (
    create_product_mission,
    summarize_product_missions,
    export_to_kaizen_mission_dry_run,
)

if __name__ == "__main__":
    mission = create_product_mission(
        idea="Primeira missao Product Factory do K-OS",
        product_type="saas",
        target_user="pequenos negocios que precisam de automacao e marketing",
        market="SaaS operacional com IA modular",
        priority="medium",
        source="phase51_runner"
    )

    print(json.dumps({
        "status": "PHASE51_PRODUCT_FACTORY_MISSION_CREATED",
        "mission_id": mission.get("mission_id"),
        "title": mission.get("title"),
        "product_type": mission.get("product_type"),
        "tasks_count": len(mission.get("tasks", [])),
        "summary": summarize_product_missions(limit=10),
        "export_dry_run": export_to_kaizen_mission_dry_run(mission),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
