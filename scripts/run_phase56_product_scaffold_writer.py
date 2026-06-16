from pathlib import Path
import sys
import json
import os

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.scaffold_writer import run_latest_scaffold_writer, CONFIRMATION_PHRASE

if __name__ == "__main__":
    confirmation = os.environ.get("KOS_PRODUCT_SCAFFOLD_CONFIRMATION", "")
    execute = os.environ.get("KOS_PRODUCT_SCAFFOLD_EXECUTE", "false").lower() == "true"

    result = run_latest_scaffold_writer(
        confirmation=confirmation,
        dry_run=not execute
    )

    print(json.dumps({
        "status": "PHASE56_PRODUCT_SCAFFOLD_WRITER_COMPLETED",
        "result_status": result.get("status"),
        "dry_run": result.get("dry_run"),
        "confirmation_valid": result.get("confirmation_valid"),
        "created_files_count": len(result.get("created_files", [])),
        "created_directories_count": len(result.get("created_directories", [])),
        "required_confirmation": CONFIRMATION_PHRASE,
        "real_action_executed": result.get("real_action_executed", False),
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))