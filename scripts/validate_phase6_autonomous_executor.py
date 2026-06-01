from pathlib import Path
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]

required = [
    "k_atlas/autonomous_executor/autonomous_loop.py",
    "k_atlas/whiteboard/board_store.py",
    "k_atlas/executive_planner.py",
    "k_atlas/artifact_builder.py",
    "k_atlas/command_autopilot.py",
    "k_atlas/action_channel_router.py",
    "reports/KOS_PHASE6_AUTONOMOUS_EXECUTOR_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

for module in [
    "k_atlas.autonomous_executor",
    "k_atlas.whiteboard.board_model",
    "k_atlas.executive_planner",
    "k_atlas.command_autopilot",
    "k_atlas.action_channel_router",
]:
    importlib.import_module(module)

data = json.loads((ROOT / "reports" / "KOS_PHASE6_AUTONOMOUS_EXECUTOR_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 6"

print("[OK] fase 6 autonomous executor")
print("STATUS: PRONTO FASE 6")
