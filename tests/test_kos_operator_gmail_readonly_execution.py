from __future__ import annotations

import ast
from pathlib import Path

from scripts.kos_operator_intent_router import route_intent


ROOT = Path(__file__).resolve().parents[1]
CHAT = ROOT / "pages" / "KOS_Operator_Chat.py"


def read_chat() -> str:
    return CHAT.read_text(encoding="utf-8-sig")


def test_router_allows_gmail_status_and_audit_readonly():
    status = route_intent("Gmail está conectado?")
    assert status["intent"] == "gmail_status"
    assert status["action_allowed"] is True
    assert status["execution_mode"] == "local_readonly"
    assert "run_gmail_operator.py --mode status --profile rogger" in status["suggested_command"]

    audit = route_intent("audite meus emails recentes")
    assert audit["intent"] == "gmail_audit"
    assert audit["action_allowed"] is True
    assert audit["execution_mode"] == "local_readonly"
    assert "--mode report --profile rogger" in audit["suggested_command"]
    assert "--max-results 20" in audit["suggested_command"]


def test_router_blocks_gmail_modifying_request_with_human_gate():
    result = route_intent("apague emails antigos")
    assert result["intent"] == "gmail_modify_blocked"
    assert result["action_allowed"] is False
    assert result["requires_human_gate"] is True
    assert "modifying Gmail is blocked" in result["reason"]


def test_operator_chat_calls_gmail_operator_only_in_readonly_modes():
    text = read_chat()
    assert "scripts/run_gmail_operator.py" in text
    assert '"status"' in text
    assert '"report"' in text
    assert '"digest"' in text
    assert '"rogger"' in text
    assert '"newer_than:7d"' in text
    assert '"20"' in text
    assert '"30"' in text

    forbidden_modes = ['"send"', '"trash"', '"delete"', '"modify"', '"read"']
    gmail_section = text[text.index("def run_kos_gmail_operator_readonly") : text.index("def build_kos_operator_intent_router_answer")]
    for marker in forbidden_modes:
        assert marker not in gmail_section


def test_operator_chat_has_no_secret_markers():
    text = read_chat().lower()
    for marker in ["token", "client_secret", "refresh_token", "access_token"]:
        assert marker not in text


def test_operator_chat_does_not_call_mutating_email_actions():
    tree = ast.parse(read_chat())
    forbidden_attrs = {"send", "trash", "delete", "modify"}
    calls = {
        node.func.attr.lower()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not forbidden_attrs.intersection(calls)
