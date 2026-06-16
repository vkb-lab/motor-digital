from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission, summarize_blueprints

if __name__ == "__main__":
    create_product_mission(
        idea="Blueprint demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase52_runner"
    )

    result = generate_blueprint_from_latest_mission()

    print(json.dumps({
        "status": "PHASE52_PRODUCT_BLUEPRINT_GENERATED",
        "result_status": result.get("status"),
        "blueprint_id": result.get("blueprint", {}).get("blueprint_id"),
        "title": result.get("blueprint", {}).get("title"),
        "product_type": result.get("blueprint", {}).get("product_type"),
        "summary": summarize_blueprints(limit=10),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
