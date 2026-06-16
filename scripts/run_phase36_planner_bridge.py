from k_atlas.kaizen.planner_bridge import run_planner_bridge
import json

if __name__ == "__main__":
    result = run_planner_bridge(
        mission="Consolidar autonomia segura do K-OS com Codex/Ollama em modo dry-run.",
        mission_id="KOS-PHASE36-DEFAULT"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
