from pathlib import Path
import json

from k_atlas.autonomous_executor import run_autonomous_command

ROOT = Path(__file__).resolve().parents[1]

DEMO_COMMAND = "Crie uma campanha para Parada Atlantida com landing page, QR Code, post Instagram, criativo visual e fila de publicacao."

def run_autopilot_demo():
    result = run_autonomous_command(DEMO_COMMAND)
    out = ROOT / "reports" / "KOS_PHASE6_AUTONOMOUS_DEMO_RESULT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
