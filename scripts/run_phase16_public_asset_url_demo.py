from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.public_asset_bridge import run_phase16_public_url_demo

result = run_phase16_public_url_demo()
print(result["status"])
print("image_url_for_instagram:", result.get("image_url_for_instagram", ""))
print("instagram_publish_executed:", result.get("instagram_publish_executed"))
