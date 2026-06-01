from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.ig_final_run import run_phase14_final_check_demo

result = run_phase14_final_check_demo()
print(result["status"])
print("real_action_executed:", result["real_action_executed"])
print("external_call_executed:", result["external_call_executed"])
