from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/public_asset_bridge/__init__.py",
    "k_atlas/public_asset_bridge/vercel_asset_bridge.py",
    "k_atlas/public_asset_bridge/public_url_runner.py",
    "pages/KOS_Public_Image_URL_Bridge.py",
    "pages/KOS_Instagram_Image_URL_Ready.py",
    "reports/KOS_PHASE16_PUBLIC_ASSET_URL_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.public_asset_bridge")

data = json.loads((ROOT / "reports/KOS_PHASE16_PUBLIC_ASSET_URL_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 16"
assert data["instagram_publish_executed"] is False

print("[OK] fase 16 public asset url bridge")
print("STATUS: PRONTO FASE 16")
