from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/live_onboarding/platform_registry.py",
    "k_atlas/live_onboarding/platform_requirements.py",
    "k_atlas/vault_presence/env_presence_checker.py",
    "k_atlas/real_execution_gate.py",
    "k_atlas/command_autopilot_live_preview.py",
    "pages/KOS_Live_Onboarding.py",
    "pages/KOS_Connector_Readiness.py",
    "pages/KOS_Approval_Gate.py",
    "reports/KOS_PHASE7_LIVE_ONBOARDING_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

for module in [
    "k_atlas.live_onboarding",
    "k_atlas.vault_presence.env_presence_checker",
    "k_atlas.real_execution_gate",
    "k_atlas.command_autopilot_live_preview",
]:
    importlib.import_module(module)

data = json.loads((ROOT / "reports/KOS_PHASE7_LIVE_ONBOARDING_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 7"

print("[OK] fase 7 live onboarding")
print("STATUS: PRONTO FASE 7")
