from pathlib import Path
import json
from datetime import datetime, timezone

from k_atlas.ig_real_gate.publisher_gate import build_ig_publish_package, execute_ig_real_publish
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness
from k_atlas.ig_first_post.post_spec import build_first_post_spec
from k_atlas.ig_first_post.public_asset_check import inspect_public_asset
from k_atlas.ig_first_post.arming_gate import inspect_phase12_arming

ROOT = Path(__file__).resolve().parents[2]

def _write_report(path_name: str, data: dict):
    path = ROOT / "reports" / path_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data

def build_first_post_package(
    client_id: str = "parada_atlantida",
    campaign_name: str = "campanha_lancamento_parada_atlantida",
    image_url: str = "https://placehold.co/1080x1080/png",
    caption: str = "Primeiro teste controlado preparado pelo K-OS."
):
    spec = build_first_post_spec(client_id, campaign_name, image_url, caption)
    asset = inspect_public_asset(image_url)
    readiness = inspect_ig_real_readiness()
    arming = inspect_phase12_arming()

    ig_package = build_ig_publish_package(
        client_id=client_id,
        campaign_name=campaign_name,
        image_url=image_url,
        caption=caption,
    )

    package = {
        "status": "READY_FOR_FINAL_ARMING" if asset["status"] == "ASSET_URL_READY" else "WAITING_ASSET_FIX",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "spec": spec,
        "asset": asset,
        "readiness": readiness,
        "arming": arming,
        "ig_package": ig_package,
        "real_action_executed": False,
        "external_call_executed": False,
        "manual_final_ok_required": True,
        "next_step": "Para executar real, configurar ambiente e armar KOS_PHASE12_REAL_RUN=YES_I_CONFIRM.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_report("KOS_PHASE12_IG_FIRST_POST_PACKAGE.json", package)

def execute_first_post_if_armed(package: dict):
    arming = inspect_phase12_arming()

    if not arming["armed"]:
        result = {
            "status": "BLOCKED_BY_PHASE12_ARMING",
            "reason": "Fase 12 nao armada para execucao real.",
            "arming": arming,
            "package_status": package.get("status"),
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_report("KOS_PHASE12_IG_FIRST_POST_RESULT.json", result)

    result = execute_ig_real_publish(package["ig_package"])
    final = {
        "status": result.get("status"),
        "result": result,
        "real_action_executed": result.get("real_action_executed", False),
        "external_call_executed": result.get("external_call_executed", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return _write_report("KOS_PHASE12_IG_FIRST_POST_RESULT.json", final)

def run_phase12_first_post_demo():
    package = build_first_post_package()
    result = execute_first_post_if_armed(package)
    demo = {
        "status": "PHASE12_DEMO_READY",
        "package": package,
        "result": result,
        "real_action_executed": result.get("real_action_executed", False),
        "external_call_executed": result.get("external_call_executed", False),
    }
    return _write_report("KOS_PHASE12_IG_FIRST_POST_DEMO.json", demo)
