from pathlib import Path
from k_atlas.creative_asset_publisher import build_campaign_asset, inspect_public_asset_url, build_instagram_asset_handoff

def test_campaign_asset_png_created():
    asset = build_campaign_asset()
    path = Path(asset["local_png_path"])
    assert asset["status"] == "CREATIVE_ASSET_READY"
    assert path.exists()
    assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

def test_public_url_check_safe():
    asset = build_campaign_asset()
    result = inspect_public_asset_url(asset)
    assert result["real_action_executed"] is False
    assert result["external_call_executed"] is False
    assert result["status"] in ["WAITING_PUBLIC_BASE_URL", "PUBLIC_ASSET_URL_READY"]

def test_handoff_no_real_action():
    result = build_instagram_asset_handoff()
    assert result["real_action_executed"] is False
    assert result["external_call_executed"] is False
