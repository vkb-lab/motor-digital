from pathlib import Path
import sys
import json
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = [
    "k_atlas/ig_first_post/__init__.py",
    "k_atlas/ig_first_post/post_spec.py",
    "k_atlas/ig_first_post/public_asset_check.py",
    "k_atlas/ig_first_post/arming_gate.py",
    "k_atlas/ig_first_post/first_post_runner.py",
    "pages/KOS_Instagram_First_Post_Test.py",
    "pages/KOS_Instagram_Final_Arming_Check.py",
    "reports/KOS_PHASE12_IG_FIRST_POST_STATUS.json",
]

for item in required:
    assert (ROOT / item).exists(), f"{item} nao existe"

importlib.import_module("k_atlas.ig_first_post")

data = json.loads((ROOT / "reports/KOS_PHASE12_IG_FIRST_POST_STATUS.json").read_text(encoding="utf-8-sig"))
assert data["status"] == "PRONTO FASE 12"
assert data["real_action_executed"] is False

print("[OK] fase 12 instagram first post")
print("STATUS: PRONTO FASE 12")
