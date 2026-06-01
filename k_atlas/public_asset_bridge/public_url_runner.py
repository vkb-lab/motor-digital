from pathlib import Path
import json
from datetime import datetime, timezone

from k_atlas.creative_asset_publisher import inspect_public_asset_url, build_instagram_asset_handoff
from k_atlas.public_asset_bridge.vercel_asset_bridge import run_vercel_asset_bridge

ROOT = Path(__file__).resolve().parents[2]

def _write_json(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def build_phase16_public_url_package(attempt_deploy: bool = True):
    deploy_result = run_vercel_asset_bridge() if attempt_deploy else {
        "status": "DEPLOY_SKIPPED",
        "real_action_executed": False,
        "external_call_executed": False,
    }

    url_check = inspect_public_asset_url()
    handoff = build_instagram_asset_handoff()

    package = {
        "status": "READY_FOR_INSTAGRAM_REAL_IMAGE" if handoff.get("image_url_for_instagram") else "WAITING_PUBLIC_IMAGE_URL",
        "deploy_result": deploy_result,
        "url_check": url_check,
        "handoff": handoff,
        "image_url_for_instagram": handoff.get("image_url_for_instagram", ""),
        "real_action_executed": False,
        "instagram_publish_executed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_PACKAGE.json", package)

def run_phase16_public_url_demo():
    result = build_phase16_public_url_package(attempt_deploy=True)
    return _write_json("reports/KOS_PHASE16_PUBLIC_ASSET_URL_DEMO.json", result)
