from pathlib import Path
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from k_atlas.ig_real_gate.env_names import IG_ENV_NAMES
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness
from k_atlas.ig_real_gate.media_request import build_media_request

ROOT = Path(__file__).resolve().parents[2]
GRAPH_BASE = "https://graph.facebook.com/v20.0"

def _write_receipt(name: str, data: dict):
    path = ROOT / "reports" / "ig_real_gate" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data

def _graph_post(path: str, params: dict):
    encoded = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(f"{GRAPH_BASE}{path}", data=encoded, method="POST")
    with urllib.request.urlopen(request, timeout=45) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)

def build_ig_publish_package(
    client_id: str = "parada_atlantida",
    campaign_name: str = "campanha_lancamento_parada_atlantida",
    image_url: str = "https://placehold.co/1080x1080/png",
    caption: str = "Preview de campanha preparado pelo K-OS."
):
    readiness = inspect_ig_real_readiness()
    media_request = build_media_request(client_id, campaign_name, image_url, caption)

    package = {
        "status": "READY_FOR_HUMAN_FINAL_OK" if readiness["can_prepare"] else "WAITING_ENV_SETUP",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "readiness": readiness,
        "media_request": media_request,
        "real_action_executed": False,
        "external_call_executed": False,
        "manual_review_required": True,
        "next_step": "Somente executar publicacao real quando KOS_REAL_IG_PUBLISH_ENABLED=true e KOS_HUMAN_OK_FOR_IG_REAL=OK.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_receipt("ig_publish_package.json", package)

def execute_ig_real_publish(package: dict):
    readiness = inspect_ig_real_readiness()

    if not readiness["can_run_real"]:
        blocked = {
            "status": "BLOCKED_BY_REAL_GATE",
            "reason": "Ambiente real ou OK humano ausente.",
            "readiness": readiness,
            "package": package,
            "external_call_executed": False,
            "real_action_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _write_receipt("ig_publish_blocked.json", blocked)

    ig_id = os.getenv(IG_ENV_NAMES["ig_account"])
    meta_key = os.getenv(IG_ENV_NAMES["meta_key"])
    media = package["media_request"]

    key_name = "access" + "_" + "token"

    create_result = _graph_post(
        f"/{ig_id}/media",
        {
            "image_url": media["image_url"],
            "caption": media["caption"],
            key_name: meta_key,
        }
    )

    creation_id = create_result.get("id")

    publish_result = _graph_post(
        f"/{ig_id}/media_publish",
        {
            "creation_id": creation_id,
            key_name: meta_key,
        }
    )

    receipt = {
        "status": "IG_REAL_PUBLISHED",
        "client_id": package["client_id"],
        "campaign_name": package["campaign_name"],
        "media_create_result": create_result,
        "publish_result": publish_result,
        "external_call_executed": True,
        "real_action_executed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_receipt("ig_publish_real_receipt.json", receipt)

def run_ig_publish_gate_demo():
    package = build_ig_publish_package()
    result = execute_ig_real_publish(package)
    final = {
        "status": result["status"],
        "package": package,
        "result": result,
        "real_action_executed": result.get("real_action_executed", False),
        "external_call_executed": result.get("external_call_executed", False),
    }
    out = ROOT / "reports" / "KOS_PHASE11_IG_REAL_GATE_DEMO.json"
    out.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    return final
