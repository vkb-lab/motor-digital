from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.product_qa_gate import refresh_product_qa_gate, get_latest_product_qa_report

if __name__ == "__main__":
    result = refresh_product_qa_gate()
    latest = get_latest_product_qa_report()

    print(json.dumps({
        "status": "PHASE59_PRODUCT_QA_GATE_COMPLETED",
        "result": result,
        "latest_status": latest.get("status"),
        "qa_status": result.get("qa_status"),
        "products_count": result.get("products_count", 0),
        "passed_count": result.get("passed_count", 0),
        "attention_required_count": result.get("attention_required_count", 0),
        "critical_count": result.get("critical_count", 0),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))