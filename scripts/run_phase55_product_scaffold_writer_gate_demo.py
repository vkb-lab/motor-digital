from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission
from k_atlas.product_factory.build_plan import generate_build_plan_from_latest_blueprint
from k_atlas.product_factory.scaffold_preview import generate_scaffold_preview_from_latest_build_plan
from k_atlas.product_factory.scaffold_writer_gate import generate_gate_from_latest_scaffold_preview, summarize_writer_gate

if __name__ == "__main__":
    create_product_mission(
        idea="Writer gate demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase55_runner"
    )

    generate_blueprint_from_latest_mission()
    generate_build_plan_from_latest_blueprint()
    generate_scaffold_preview_from_latest_build_plan()
    result = generate_gate_from_latest_scaffold_preview()

    print(json.dumps({
        "status": "PHASE55_PRODUCT_SCAFFOLD_WRITER_GATE_GENERATED",
        "result_status": result.get("status"),
        "gate_id": result.get("gate", {}).get("gate_id"),
        "files_count": result.get("gate", {}).get("files_count"),
        "write_product_files_allowed_now": False,
        "summary": summarize_writer_gate(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
