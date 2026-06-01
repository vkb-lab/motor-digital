from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]

path = ROOT / "reports" / "KOS_PHASE15_INSTAGRAM_ASSET_HANDOFF.json"
if not path.exists():
    raise SystemExit("Handoff da Fase 15 nao existe. Rode scripts/run_phase15_creative_asset_demo.py")

data = json.loads(path.read_text(encoding="utf-8-sig"))
url = data.get("image_url_for_instagram", "")

out = ROOT / "reports" / "KOS_PHASE15_IMAGE_URL_FOR_INSTAGRAM.txt"
out.write_text(url, encoding="utf-8")

print(url if url else "WAITING_PUBLIC_URL")
