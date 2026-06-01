from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/safe_execution/__init__.py",
    "k_atlas/safe_execution/approved_runner.py",
    "k_atlas/safe_execution/channel_queue.py",
    "k_atlas/safe_execution/channel_executor.py",
    "pages/KOS_Approved_Safe_Execution.py",
    "pages/KOS_Safe_Execution_Queue.py",
    "pages/KOS_Safe_Execution_Review.py",
    "reports/KOS_PHASE9_SAFE_EXECUTION_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.safe_execution")

data = json.loads((ROOT / "reports/KOS_PHASE9_SAFE_EXECUTION_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 9"
assert data["real_action_executed"] is False

print("[OK] fase 9 safe execution")
print("STATUS: PRONTO FASE 9")
