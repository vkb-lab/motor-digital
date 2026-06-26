from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.kos_operator_intent_router import route_intent


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "memory" / "kos_governance" / "KOS_OPERATOR_CAPABILITY_POLICY.json"


def test_operator_capability_policy_declares_commissioning_matrix():
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    allowed = set(data["allowed_readonly"])
    assert {
        "gmail_digest",
        "gmail_status",
        "brain_provider_status",
        "google_toolbelt_audit",
        "work_sequence_list",
        "work_sequence_plan",
        "navigation_status",
        "render_readiness_status",
        "personal_data_estate_status",
        "local_storage_status",
        "origin_core_status",
    }.issubset(allowed)
    assert "generate_reports" in data["allowed_local_generation"]
    assert "gmail_send" in data["requires_human_gate"]
    assert "local_runtime_direct_access" in data["blocked"]


def test_operator_router_opens_safe_readonly_status_ports():
    cases = {
        "fonte de verdade do K-OS": "origin_core_status",
        "quais ferramentas Google existem?": "google_toolbelt_status",
        "listar sequencias de trabalho": "work_sequence_list",
        "plano personal_data_foundation": "work_sequence_plan",
        "status navegacao customizada": "navigation_status",
        "status dados pessoais": "personal_data_estate_status",
        "local storage status": "local_storage_status",
        "render readiness": "render_readiness_status",
    }
    for text, intent in cases.items():
        result = route_intent(text)
        assert result["intent"] == intent
        assert result["action_allowed"] is True
        assert result["execution_mode"] == "local_readonly"
        assert result["requires_human_gate"] is False


def test_gmail_status_output_is_sanitized_readonly():
    result = subprocess.run(
        [sys.executable, "scripts/run_gmail_operator.py", "--mode", "status", "--profile", "rogger"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "KOS_GMAIL_OPERATOR_STATUS"
    assert data["paths_redacted"] is True
    assert "client_secret_path" not in data
    assert "token_path" not in data
