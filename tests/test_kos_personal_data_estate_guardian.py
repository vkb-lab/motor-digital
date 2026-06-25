from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_personal_data_estate_registry_and_skill_exist():
    registry = ROOT / "memory" / "kos_governance" / "KOS_PERSONAL_DATA_ESTATE_REGISTRY.json"
    skill = ROOT / "memory" / "kos_skills" / "KOS_SKILL_PERSONAL_DATA_ESTATE_GUARDIAN_V1.md"
    data = json.loads(registry.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_PERSONAL_DATA_ESTATE_GUARDIAN_READY"
    assert "identity" in data["protected_domains"]
    assert skill.exists()


def test_personal_data_estate_status_script_is_safe_json():
    script = ROOT / "scripts" / "run_personal_data_estate_status.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    completed = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True, capture_output=True, text=True)
    data = json.loads(completed.stdout)
    assert data["status"] == "KOS_PERSONAL_DATA_ESTATE_STATUS_READY"
    assert data["external_api_accessed"] is False
    assert data["secrets_read"] is False
