from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.product_registry import refresh_product_registry, get_latest_registry

if __name__ == "__main__":
    result = refresh_product_registry()
    latest = get_latest_registry()

    print(json.dumps({
        "status": "PHASE57_PRODUCT_RUNTIME_REGISTRY_COMPLETED",
        "result": result,
        "latest_status": latest.get("status"),
        "products_count": result.get("products_count", 0),
        "safe_products_count": result.get("safe_products_count", 0),
        "attention_required_count": result.get("attention_required_count", 0),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))