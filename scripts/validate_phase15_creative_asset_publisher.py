from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/creative_asset_publisher/__init__.py",
    "k_atlas/creative_asset_publisher/png_canvas.py",
    "k_atlas/creative_asset_publisher/asset_builder.py",
    "k_atlas/creative_asset_publisher/asset_url.py",
    "k_atlas/creative_asset_publisher/asset_handoff.py",
    "pages/KOS_Creative_Asset_Factory.py",
    "pages/KOS_Public_Asset_URL_Check.py",
    "pages/KOS_Instagram_Asset_Handoff.py",
    "reports/KOS_PHASE15_CREATIVE_ASSET_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.creative_asset_publisher")

data = json.loads((ROOT / "reports/KOS_PHASE15_CREATIVE_ASSET_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 15"
assert data["real_action_executed"] is False

print("[OK] fase 15 creative asset publisher")
print("STATUS: PRONTO FASE 15")
