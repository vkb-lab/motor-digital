from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_app_is_local_command_center():
    text = read("app.py")
    assert "K-OS Local Command Center" in text
    assert "Nucleo oficial" in text or "Núcleo oficial" in text
    assert "Modulos avancados / legado" in text or "Módulos avançados / legado" in text


def test_app_does_not_reference_sensitive_runtime_or_gmail_secrets():
    lower = read("app.py").lower()
    assert "local_runtime" not in lower
    assert "token_gmail" not in lower
    assert "client_secret" not in lower
    assert "gmail.googleapis.com" not in lower
    assert "googleapiclient" not in lower


def test_status_script_compiles_and_returns_json():
    script = ROOT / "scripts" / "run_kos_local_home_status.py"
    subprocess.run([sys.executable, "-m", "py_compile", str(script)], cwd=ROOT, check=True)
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(completed.stdout)
    assert data["status"] == "KOS_LOCAL_HOME_STATUS_READY"
    assert data["entrypoint"] == "app.py"
    assert data["recommended_port"] == 8501
    assert data["guardrails"]["gmail_api_called"] is False
    assert data["guardrails"]["external_action_executed"] is False


def test_home_references_ten_official_core_items():
    text = read("app.py")
    expected = [
        "KOS Operator Chat",
        "KOS Unified Command Cockpit",
        "KOS Runtime Health",
        "KOS Mission Queue",
        "KOS Safe Execution Review",
        "KOS Approval Gate / Human Approval",
        "KOS Gmail Status",
        "KOS Google Toolbelt Status",
        "KOS Brain Provider Status",
        "KOS Render Read-Only Mobile Runtime",
    ]
    for item in expected:
        assert item in text


def test_app_ksocial_gateway_is_not_principal_home_or_port_owner():
    text = read("app_ksocial_gateway.py").lower()
    assert "k-os local command center" not in text
    assert "server.port 8501" not in text
    assert "--server.port" not in text
