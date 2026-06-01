from pathlib import Path
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

def build_confirmation_package(client_id: str, campaign_name: str, asset_pack: dict):
    data = {
        "status": "PENDING_FINAL_APPROVAL",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "summary": "Pacote de lancamento preparado para revisao humana.",
        "asset_pack": asset_pack,
        "real_actions_enabled": False,
        "real_action_executed": False,
        "manual_approval_required": True,
        "next_human_decision": "OK para seguir para execucao controlada ou ajustar campanha.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    path = ROOT / "reports" / "KOS_PHASE8_CONFIRMATION_DEMO.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data
