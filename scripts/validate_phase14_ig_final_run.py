from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/ig_final_run/__init__.py",
    "k_atlas/ig_final_run/final_gate.py",
    "k_atlas/ig_final_run/final_runner.py",
    "pages/KOS_Instagram_Final_Run_Gate.py",
    "pages/KOS_Instagram_Real_Send_Control.py",
    "reports/KOS_PHASE14_IG_FINAL_RUN_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.ig_final_run")

data = json.loads((ROOT / "reports/KOS_PHASE14_IG_FINAL_RUN_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 14"
assert data["real_action_executed"] is False

print("[OK] fase 14 instagram final run")
print("STATUS: PRONTO FASE 14")
