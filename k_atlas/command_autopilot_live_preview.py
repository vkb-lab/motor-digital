from pathlib import Path
import json
from k_atlas.command_autopilot import run_autopilot_demo
from k_atlas.autonomous_executor.live_gate_integration import attach_live_gate_preview

ROOT = Path(__file__).resolve().parents[1]

def run_live_gate_autopilot_preview():
    result = attach_live_gate_preview(run_autopilot_demo())
    out = ROOT / "reports" / "KOS_PHASE7_APPROVAL_GATE_DEMO.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
