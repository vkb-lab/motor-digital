from __future__ import annotations

from pathlib import Path

from scripts.kos_operator_intent_router import route_intent
from scripts.run_gmail_operator import classify_gmail_digest_category


ROOT = Path(__file__).resolve().parents[1]
CHAT = ROOT / "pages" / "KOS_Operator_Chat.py"


def read_chat() -> str:
    return CHAT.read_text(encoding="utf-8-sig")


def test_gmail_digest_intent_is_distinct_from_status():
    digest = route_intent("verifique meu email")
    assert digest["intent"] == "gmail_digest"
    assert digest["action_allowed"] is True
    assert digest["execution_mode"] == "local_readonly"
    assert "--mode report --profile rogger" in digest["suggested_command"]
    assert "--max-results 30" in digest["suggested_command"]

    status = route_intent("Gmail está conectado?")
    assert status["intent"] == "gmail_status"
    assert "--mode status --profile rogger" in status["suggested_command"]


def test_gmail_modify_requests_are_not_allowed_readonly():
    result = route_intent("apague emails antigos")
    assert result["intent"] == "gmail_modify_blocked"
    assert result["action_allowed"] is False
    assert result["requires_human_gate"] is True

    reply = route_intent("responda email para esse cliente")
    assert reply["intent"] == "gmail_modify_blocked"
    assert reply["action_allowed"] is False


def test_gmail_digest_category_classifier():
    assert classify_gmail_digest_category("Render startup credits cloud program") == "oportunidades/startup/crédito"
    assert classify_gmail_digest_category("Mercado Livre promoção oferta cupom") == "promoções/ofertas"
    assert classify_gmail_digest_category("invoice fatura pagamento receipt") == "financeiro/cobrança"
    assert classify_gmail_digest_category("pdf documento contrato anexado") == "documentos/anexos"


def test_operator_chat_handles_gmail_digest_readonly():
    text = read_chat()
    assert '"gmail_digest"' in text
    assert "run_kos_gmail_operator_readonly(\"digest\")" in text
    assert '"--max-results"' in text
    assert '"30"' in text
    assert "_kos_build_gmail_digest_response" in text


def test_digest_path_does_not_use_mutating_gmail_modes():
    text = read_chat()
    section = text[text.index("def run_kos_gmail_operator_readonly") : text.index("def _kos_safe_email_example")]
    for marker in ['"send"', '"trash"', '"delete"', '"modify"', '"read"', "archive", "move"]:
        assert marker not in section.lower()


def test_operator_chat_has_no_secret_markers():
    text = read_chat().lower()
    for marker in ["token", "client_secret", "refresh_token", "access_token"]:
        assert marker not in text
