from pathlib import Path
import importlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_phase2_required_modules_import():
    for module_name in [
        "k_atlas.permissions",
        "k_atlas.approval_flow",
        "k_atlas.task_queue",
        "k_atlas.orchestrator",
        "k_atlas.agent_runtime",
    ]:
        importlib.import_module(module_name)


def test_phase2_permission_contract():
    from k_atlas.permissions import check_permission, require_permission, PermissionManager

    assert check_permission("CampaignAgent", "EXECUTE").allowed is True
    assert require_permission("CampaignAgent", "EXTERNAL", external=True).status == "PENDING_APPROVAL"
    assert PermissionManager().check_permission("CampaignAgent", "EXECUTE").allowed is True


def test_phase2_orchestrator_delegates_task():
    from k_atlas.orchestrator import Orchestrator

    task = Orchestrator().delegate_task("CampaignAgent", "create_campaign", {"name": "demo"})
    assert task["agent"] == "CampaignAgent"
    assert task["status"] == "QUEUED"


def test_phase2_validate_script_passes():
    script = ROOT / "scripts" / "validate_phase2.py"
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "STATUS: FASE 2 OK" in result.stdout


def test_phase2_status_report_exists():
    status_path = ROOT / "reports" / "KOS_PHASE2_STATUS.json"
    report_path = ROOT / "reports" / "KOS_PHASE2_REPORT.md"
    assert status_path.exists()
    assert report_path.exists()
    data = json.loads(status_path.read_text(encoding="utf-8-sig"))
    assert data["status"] == "PRONTO FASE 2"
