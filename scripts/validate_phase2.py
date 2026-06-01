from pathlib import Path
import importlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required_files = [
    "k_atlas/permissions.py",
    "k_atlas/approval_flow.py",
    "k_atlas/task_queue.py",
    "k_atlas/orchestrator.py",
    "k_atlas/agent_runtime.py",
    "reports/KOS_PHASE2_STATUS.json",
    "reports/KOS_PHASE2_REPORT.md",
]

for file_path in required_files:
    path = ROOT / file_path
    if not path.exists():
        raise SystemExit(f"[FAIL] {file_path} nao existe")

for module_name in [
    "k_atlas.permissions",
    "k_atlas.approval_flow",
    "k_atlas.task_queue",
    "k_atlas.orchestrator",
    "k_atlas.agent_runtime",
]:
    importlib.import_module(module_name)

from k_atlas.permissions import check_permission
from k_atlas.orchestrator import Orchestrator

decision = check_permission("CampaignAgent", "EXECUTE")
if decision.allowed is not True:
    raise SystemExit("[FAIL] CampaignAgent sem EXECUTE")

external = check_permission("CampaignAgent", "EXTERNAL", external=True)
if external.status != "PENDING_APPROVAL":
    raise SystemExit("[FAIL] Acao externa nao ficou PENDING_APPROVAL")

task = Orchestrator().delegate_task("CampaignAgent", "create_campaign", {"name": "demo"})
if task["status"] != "QUEUED":
    raise SystemExit("[FAIL] Orchestrator nao criou task QUEUED")

data = json.loads((ROOT / "reports" / "KOS_PHASE2_STATUS.json").read_text(encoding="utf-8-sig"))
if data.get("status") != "PRONTO FASE 2":
    raise SystemExit("[FAIL] Status JSON invalido")

print("[OK] fase 2 artifacts")
print("[OK] fase 2 imports")
print("[OK] fase 2 permissions")
print("[OK] fase 2 orchestrator")
print("STATUS: FASE 2 OK")
