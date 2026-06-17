from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.product_export_packager import (
    refresh_product_export_packager,
    get_latest_product_export_packager_report,
)

if __name__ == "__main__":
    result = refresh_product_export_packager()
    latest = get_latest_product_export_packager_report()

    print(json.dumps({
        "status": "PHASE63_PRODUCT_EXPORT_PACKAGER_COMPLETED",
        "result": result,
        "latest_status": latest.get("status"),
        "products_count": result.get("products_count", 0),
        "ready_count": result.get("ready_count", 0),
        "attention_required_count": result.get("attention_required_count", 0),
        "package_creation_allowed": False,
        "zip_creation_allowed": False,
        "deploy_allowed": False,
        "paid_ai_allowed": False,
        "instagram_publish_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))