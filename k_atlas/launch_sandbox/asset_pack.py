from pathlib import Path
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

def _slug(value: str):
    value = str(value).lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "launch"

def build_asset_pack(plan: dict, previews: dict):
    data = {
        "status": "PENDING_APPROVAL",
        "client_id": plan["client_id"],
        "campaign_name": plan["campaign_name"],
        "objective": plan["objective"],
        "previews": previews,
        "real_actions_enabled": False,
        "manual_approval_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    name = f"{_slug(plan['client_id'])}_{_slug(plan['campaign_name'])}_asset_pack.json"
    path = ROOT / "reports" / "launch_sandbox" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data
