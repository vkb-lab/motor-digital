from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/deploy_bridge/__init__.py",
    "k_atlas/deploy_bridge/deploy_manifest.py",
    "k_atlas/deploy_bridge/static_exporter.py",
    "k_atlas/deploy_bridge/vercel_gate.py",
    "vercel.json",
    "public/kos/index.html",
    "public/kos/status.json",
    "pages/KOS_Production_Deploy_Bridge.py",
    "pages/KOS_Vercel_Readiness.py",
    "reports/KOS_PHASE10_DEPLOY_BRIDGE_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.deploy_bridge")

data = json.loads((ROOT / "reports/KOS_PHASE10_DEPLOY_BRIDGE_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 10"
assert data["real_publish_enabled"] is False

print("[OK] fase 10 deploy bridge")
print("STATUS: PRONTO FASE 10")
