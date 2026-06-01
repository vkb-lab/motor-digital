from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def create_execution_receipt(job_id: str, client_id: str, task_id: str, status: str = "PENDING_APPROVAL"):
    receipt = {
        "job_id": job_id,
        "client_id": client_id,
        "task_id": task_id,
        "status": status,
        "external_call_executed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = ROOT / "reports" / "execution_receipts" / f"{job_id}_{task_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    receipt["path"] = str(path)
    return receipt
