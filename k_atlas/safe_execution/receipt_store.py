from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

def save_safe_receipts(client_id: str, campaign_name: str, receipts: list):
    path = ROOT / "reports" / "safe_execution" / f"{client_id}_{campaign_name}_receipts.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "status": "SAFE_RECEIPTS_READY",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "receipts": receipts,
        "real_action_executed": False,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data
