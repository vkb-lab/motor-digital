from pathlib import Path
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for key in [
    "KOS_REAL_IG_PUBLISH_ENABLED",
    "KOS_HUMAN_OK_FOR_IG_REAL",
    "KOS_PHASE12_REAL_RUN",
    "KOS_PHASE13_REAL_RUN",
]:
    os.environ.pop(key, None)

from k_atlas.ig_live_check import run_phase13_live_check_demo

result = run_phase13_live_check_demo()
print(result["status"])
print("ready_for_real_first_post:", result["ready_for_real_first_post"])
print("real_action_executed:", result["real_action_executed"])
print("external_call_executed:", result["external_call_executed"])
