from pathlib import Path
import json
from k_atlas.live_onboarding.platform_registry import PLATFORMS
from k_atlas.live_onboarding.readiness_matrix import build_readiness_matrix
from k_atlas.live_onboarding.onboarding_plan import build_onboarding_plan
from k_atlas.live_onboarding.onboarding_state import save_onboarding_state

ROOT = Path(__file__).resolve().parents[2]

def generate_client_onboarding(client_id: str):
    plans = {p: build_onboarding_plan(client_id, p) for p in PLATFORMS}
    readiness = build_readiness_matrix(client_id)
    data = {
        "client_id": client_id,
        "status": "PENDING_APPROVAL",
        "plans": plans,
        "readiness": readiness,
        "values_saved": False,
        "real_actions_enabled": False,
        "manual_approval_required": True,
    }
    save_onboarding_state(client_id, data)

    cdir = ROOT / "clients" / client_id / "connectors"
    cdir.mkdir(parents=True, exist_ok=True)

    (cdir / "readiness_matrix.json").write_text(json.dumps(readiness, ensure_ascii=False, indent=2), encoding="utf-8")
    (cdir / "approval_policy.json").write_text(json.dumps({
        "client_id": client_id,
        "manual_approval_required": True,
        "real_publish_allowed": False,
        "real_ads_allowed": False,
        "real_google_edit_allowed": False,
        "real_dm_allowed": False,
        "real_payment_allowed": False
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return data
