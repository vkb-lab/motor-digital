from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "memory" / "kos_governance" / "KOS_OPERATOR_CAPABILITY_POLICY.json"


def test_operator_capability_policy_exists_and_classifies_gmail():
    assert POLICY.exists()
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_OPERATOR_CAPABILITY_POLICY_ACTIVE"
    assert "gmail_status" in data["allowed_readonly"]
    assert "gmail_report_limited" in data["allowed_readonly"]
    assert "permanent_delete" in data["blocked"]


def test_operator_capability_policy_separates_human_gate_from_blocked():
    data = json.loads(POLICY.read_text(encoding="utf-8"))
    assert "gmail_archive" in data["requires_human_gate"]
    assert "gmail_mark_read" in data["requires_human_gate"]
    assert "bypass_guardrails" in data["blocked"]
