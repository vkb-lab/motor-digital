from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from k_atlas.command_autopilot_live_preview import run_live_gate_autopilot_preview
print(run_live_gate_autopilot_preview()["status"])
