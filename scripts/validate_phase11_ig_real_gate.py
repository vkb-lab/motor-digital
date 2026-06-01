from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/ig_real_gate/__init__.py",
    "k_atlas/ig_real_gate/env_names.py",
    "k_atlas/ig_real_gate/readiness.py",
    "k_atlas/ig_real_gate/media_request.py",
    "k_atlas/ig_real_gate/publisher_gate.py",
    "pages/KOS_Instagram_Real_Publisher_Gate.py",
    "pages/KOS_Instagram_Real_Readiness.py",
    "reports/KOS_PHASE11_IG_REAL_GATE_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.ig_real_gate")

data = json.loads((ROOT / "reports/KOS_PHASE11_IG_REAL_GATE_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 11"
assert data["real_action_executed"] is False

print("[OK] fase 11 instagram real gate")
print("STATUS: PRONTO FASE 11")
