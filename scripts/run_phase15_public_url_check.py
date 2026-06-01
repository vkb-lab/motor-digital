from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.creative_asset_publisher import inspect_public_asset_url

result = inspect_public_asset_url()
print(json.dumps(result, ensure_ascii=False, indent=2))
