from pathlib import Path
import json
from datetime import datetime, timezone

from k_atlas.creative_asset_publisher.asset_builder import build_campaign_asset
from k_atlas.creative_asset_publisher.asset_url import inspect_public_asset_url

ROOT = Path(__file__).resolve().parents[2]

def build_instagram_asset_handoff(
    client_id: str = "parada_atlantida",
    campaign_name: str = "campanha_lancamento_parada_atlantida",
    title: str = "PARADA ATLANTIDA",
    subtitle: str = "LAN?AMENTO DIGITAL",
    cta: str = "CONFIRA AS NOVIDADES",
    caption: str = "Primeiro teste controlado da campanha Parada Atl?ntida."
):
    asset = build_campaign_asset(client_id, campaign_name, title, subtitle, cta)
    url = inspect_public_asset_url(asset)

    package = {
        "status": "READY_FOR_INSTAGRAM_URL" if url["public_url_ready"] else "WAITING_PUBLIC_URL",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "caption": caption,
        "asset": asset,
        "url": url,
        "image_url_for_instagram": url.get("public_url", ""),
        "real_action_executed": False,
        "external_call_executed": False,
        "next_step": "Se public_url estiver vazio, definir KOS_PUBLIC_BASE_URL ou fazer deploy Vercel.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    out = ROOT / "reports" / "KOS_PHASE15_INSTAGRAM_ASSET_HANDOFF.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    return package
