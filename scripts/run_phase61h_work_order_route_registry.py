from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.work_order_route_registry import get_work_order_route_registry_status

if __name__ == "__main__":
    result = get_work_order_route_registry_status()
    print(json.dumps({
        "status": "PHASE61H_WORK_ORDER_ROUTE_REGISTRY_COMPLETED",
        "registry_status": result.get("status"),
        "routes_count": result.get("routes_count"),
        "unknown_route_requires_review": True,
        "no_command_execution": True,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
    }, ensure_ascii=False, indent=2))
