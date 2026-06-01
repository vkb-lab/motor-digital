from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "reports" / "KOS_PHASE16_PUBLIC_ASSET_URL_PACKAGE.json"

if not path.exists():
    raise SystemExit("Fase 16 ainda nao gerou pacote.")

data = json.loads(path.read_text(encoding="utf-8-sig"))
print(data.get("image_url_for_instagram", "") or "WAITING_PUBLIC_IMAGE_URL")
