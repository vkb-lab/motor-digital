from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.creative_asset_publisher import build_instagram_asset_handoff

result = build_instagram_asset_handoff()
png_path = Path(result["asset"]["local_png_path"])

print(result["status"])
print("png_exists:", png_path.exists())
print("png_path:", png_path)
print("image_url_for_instagram:", result.get("image_url_for_instagram", ""))
print("real_action_executed:", result["real_action_executed"])
print("external_call_executed:", result["external_call_executed"])
