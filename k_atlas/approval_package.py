from pathlib import Path
import json
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]

def build_approval_package(client_id: str, action: str, payload: dict | None = None):
    data = {
        "client_id": client_id,
        "action": action,
        "payload": payload or {},
        "status": "PENDING_APPROVAL",
        "real_actions_blocked": True,
        "manual_approval_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = ROOT / "reports" / "live_onboarding" / f"{client_id}_{action}_approval_package.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data
