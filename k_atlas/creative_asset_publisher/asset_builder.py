from pathlib import Path
import json
import re
from datetime import datetime, timezone

from k_atlas.creative_asset_publisher.png_canvas import create_campaign_png

ROOT = Path(__file__).resolve().parents[2]

def slug(value: str):
    value = str(value).lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "asset"

def build_campaign_asset(
    client_id: str = "parada_atlantida",
    campaign_name: str = "campanha_lancamento_parada_atlantida",
    title: str = "PARADA ATLANTIDA",
    subtitle: str = "LAN?AMENTO DIGITAL",
    cta: str = "CONFIRA AS NOVIDADES"
):
    asset_id = f"{slug(client_id)}_{slug(campaign_name)}"
    png_path = ROOT / "public" / "kos" / "assets" / f"{asset_id}.png"
    meta_path = ROOT / "public" / "kos" / "assets" / f"{asset_id}.json"

    png_info = create_campaign_png(png_path, title, subtitle, cta)

    package = {
        "status": "CREATIVE_ASSET_READY",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "asset_id": asset_id,
        "title": title,
        "subtitle": subtitle,
        "cta": cta,
        "local_png_path": str(png_path),
        "public_path": f"/kos/assets/{asset_id}.png",
        "png": png_info,
        "real_action_executed": False,
        "external_call_executed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    meta_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    report_path = ROOT / "reports" / "KOS_PHASE15_CREATIVE_ASSET_PACKAGE.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    return package
