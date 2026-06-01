from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/ig_live_check/__init__.py",
    "k_atlas/ig_live_check/runtime_loader.py",
    "k_atlas/ig_live_check/env_plan.py",
    "k_atlas/ig_live_check/final_live_check.py",
    "k_atlas/ig_live_check/live_check_runner.py",
    "pages/KOS_Instagram_Live_Env_Setup.py",
    "pages/KOS_Instagram_Final_Live_Check.py",
    "reports/KOS_PHASE13_IG_LIVE_CHECK_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.ig_live_check")

data = json.loads((ROOT / "reports/KOS_PHASE13_IG_LIVE_CHECK_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 13"
assert data["real_action_executed"] is False

print("[OK] fase 13 instagram live check")
print("STATUS: PRONTO FASE 13")
