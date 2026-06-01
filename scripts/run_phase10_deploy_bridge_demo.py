from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.deploy_bridge import export_public_status, inspect_vercel_readiness

exported = export_public_status()
readiness = inspect_vercel_readiness()

result = {
    "status": "DEPLOY_BRIDGE_DEMO_READY",
    "exported": exported,
    "vercel": readiness,
    "real_publish_enabled": False,
    "external_call_executed": False,
}

out = ROOT / "reports" / "KOS_PHASE10_DEPLOY_BRIDGE_DEMO.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(result["status"])
print(readiness["status"])
