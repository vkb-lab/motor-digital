from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission
from k_atlas.product_factory.build_plan import generate_build_plan_from_latest_blueprint, summarize_build_plans

if __name__ == "__main__":
    create_product_mission(
        idea="Build plan demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase53_runner"
    )

    generate_blueprint_from_latest_mission()
    result = generate_build_plan_from_latest_blueprint()

    print(json.dumps({
        "status": "PHASE53_PRODUCT_BUILD_PLAN_GENERATED",
        "result_status": result.get("status"),
        "build_plan_id": result.get("build_plan", {}).get("build_plan_id"),
        "title": result.get("build_plan", {}).get("title"),
        "product_type": result.get("build_plan", {}).get("product_type"),
        "suggested_files_count": len(result.get("build_plan", {}).get("suggested_files", [])),
        "summary": summarize_build_plans(limit=10),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
