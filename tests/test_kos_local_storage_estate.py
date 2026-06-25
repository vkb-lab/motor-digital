from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_local_storage_registry_is_repo_scoped():
    path = ROOT / "memory" / "kos_governance" / "KOS_LOCAL_STORAGE_ESTATE_REGISTRY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_LOCAL_STORAGE_ESTATE_REGISTRY_READY"
    assert data["scope"] == "repo_declared_paths_only"
    assert "full_disk_scan" in data["forbidden_behaviors"]
    assert "local_runtime_reading" in data["forbidden_behaviors"]


def test_local_storage_status_does_not_scan_broadly():
    script = ROOT / "scripts" / "run_local_storage_estate_status.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    completed = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True, capture_output=True, text=True)
    data = json.loads(completed.stdout)
    assert data["status"] == "KOS_LOCAL_STORAGE_ESTATE_STATUS_READY"
    assert data["full_disk_scan_performed"] is False
    assert data["mass_hashing_performed"] is False
