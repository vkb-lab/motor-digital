from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/launch_sandbox/__init__.py",
    "k_atlas/launch_sandbox/launch_plan.py",
    "k_atlas/launch_sandbox/channel_preview.py",
    "k_atlas/launch_sandbox/asset_pack.py",
    "k_atlas/launch_sandbox/confirmation_package.py",
    "k_atlas/launch_sandbox/launch_runner.py",
    "pages/KOS_Launch_Sandbox.py",
    "pages/KOS_Launch_Confirmation.py",
    "reports/KOS_PHASE8_LAUNCH_SANDBOX_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

for module in [
    "k_atlas.launch_sandbox",
    "k_atlas.launch_sandbox.launch_runner",
    "k_atlas.launch_sandbox.confirmation_package",
]:
    importlib.import_module(module)

data = json.loads((ROOT / "reports/KOS_PHASE8_LAUNCH_SANDBOX_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 8"
assert data["real_actions_enabled"] is False

print("[OK] fase 8 launch sandbox")
print("STATUS: PRONTO FASE 8")
