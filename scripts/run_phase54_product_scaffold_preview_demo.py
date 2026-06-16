from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission
from k_atlas.product_factory.build_plan import generate_build_plan_from_latest_blueprint
from k_atlas.product_factory.scaffold_preview import generate_scaffold_preview_from_latest_build_plan, summarize_scaffold_previews

if __name__ == "__main__":
    create_product_mission(
        idea="Scaffold preview demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase54_runner"
    )

    generate_blueprint_from_latest_mission()
    generate_build_plan_from_latest_blueprint()
    result = generate_scaffold_preview_from_latest_build_plan()

    print(json.dumps({
        "status": "PHASE54_PRODUCT_SCAFFOLD_PREVIEW_GENERATED",
        "result_status": result.get("status"),
        "scaffold_preview_id": result.get("scaffold_preview", {}).get("scaffold_preview_id"),
        "title": result.get("scaffold_preview", {}).get("title"),
        "product_type": result.get("scaffold_preview", {}).get("product_type"),
        "files_preview_count": len(result.get("scaffold_preview", {}).get("files_preview", [])),
        "summary": summarize_scaffold_previews(limit=10),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
