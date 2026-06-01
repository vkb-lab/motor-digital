from pathlib import Path
import json
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]

def create_live_action_receipt(client_id: str, platform: str, action: str):
    data = {
        "client_id": client_id,
        "platform": platform,
        "action": action,
        "status": "PENDING_APPROVAL",
        "external_call_executed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = ROOT / "reports" / "live_action_receipts" / f"{client_id}_{platform}_{action}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data
