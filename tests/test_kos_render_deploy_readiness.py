from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_render_policy_declares_read_only_control_plane():
    path = ROOT / "memory" / "kos_governance" / "KOS_RENDER_CLOUD_RUNTIME_POLICY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_RENDER_CLOUD_RUNTIME_POLICY_READY"
    assert data["cloud_entrypoint"] == "app_render.py"
    assert "deploy_execution" in data["forbidden"]
    assert "secret_exposure" in data["forbidden"]


def test_render_readiness_status_is_no_deploy():
    script = ROOT / "scripts" / "run_render_deploy_readiness_status.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    completed = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True, capture_output=True, text=True)
    data = json.loads(completed.stdout)
    assert data["status"] == "KOS_RENDER_DEPLOY_READINESS_STATUS_READY"
    assert data["deploy_executed"] is False
    assert data["render_yaml_changed"] is False
    assert data["secrets_read"] is False
