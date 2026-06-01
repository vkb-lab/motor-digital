from pathlib import Path
import importlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_phase2_required_modules_import():
    modules = [
        "k_atlas.permissions",
        "k_atlas.approval_flow",
        "k_atlas.task_queue",
        "k_atlas.orchestrator",
        "k_atlas.agent_runtime",
    ]
    for module_name in modules:
        importlib.import_module(module_name)


def test_phase2_validate_script_passes():
    script = ROOT / "scripts" / "validate_phase2.py"
    assert script.exists()
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_phase2_status_report_exists():
    status_path = ROOT / "reports" / "KOS_PHASE2_STATUS.json"
    report_path = ROOT / "reports" / "KOS_PHASE2_REPORT.md"
    assert status_path.exists()
    assert report_path.exists()
    data = json.loads(status_path.read_text(encoding="utf-8-sig"))
    assert data.get("status") == "PRONTO FASE 2"
