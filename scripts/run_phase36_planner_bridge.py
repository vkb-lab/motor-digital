from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.planner_bridge import run_planner_bridge
import json

if __name__ == "__main__":
    result = run_planner_bridge(
        mission="Consolidar autonomia segura do K-OS com Codex/Ollama em modo dry-run.",
        mission_id="KOS-PHASE36-DEFAULT"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
