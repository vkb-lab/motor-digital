from pathlib import Path
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.pop("KOS_PHASE12_REAL_RUN", None)

from k_atlas.ig_first_post import run_phase12_first_post_demo

result = run_phase12_first_post_demo()
print(result["status"])
print("real_action_executed:", result["real_action_executed"])
print("external_call_executed:", result["external_call_executed"])
