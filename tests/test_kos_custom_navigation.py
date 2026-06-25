from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_custom_navigation_registry_declares_core_and_legacy_groups():
    path = ROOT / "memory" / "kos_governance" / "KOS_CUSTOM_NAVIGATION_REGISTRY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_CUSTOM_NAVIGATION_REGISTRY_READY"
    assert "pages/KOS_Operator_Chat.py" in data["official_core"]
    assert "duplicated gates" in data["legacy_groups_to_hide"]
    assert "do_not_change_app_py_in_this_step" in data["rules"]


def test_custom_navigation_status_is_registry_only():
    script = ROOT / "scripts" / "run_kos_navigation_status.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    completed = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True, capture_output=True, text=True)
    data = json.loads(completed.stdout)
    assert data["status"] == "KOS_CUSTOM_NAVIGATION_STATUS_READY"
    assert data["pages_moved"] is False
    assert data["pages_removed"] is False
    assert data["app_py_changed_by_this_step"] is False
