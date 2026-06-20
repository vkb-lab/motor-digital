from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase72d_files_exist():
    assert (ROOT / "pages" / "KOS_Operator_Chat.py").exists()
    assert (ROOT / "scripts" / "open_kos_operator_chat.ps1").exists()
    assert (ROOT / "KOS_START_HERE.cmd").exists()
    assert (ROOT / "config" / "kos_operator_chat_frontdoor_policy.json").exists()
    assert (ROOT / "docs" / "KOS_OPERATOR_CHAT_FRONTDOOR_V072D.md").exists()

def test_phase72d_policy_safe():
    policy = json.loads((ROOT / "config" / "kos_operator_chat_frontdoor_policy.json").read_text(encoding="utf-8-sig"))
    assert policy["purpose"] == "single_chat_frontdoor_for_operator"
    assert policy["hides_technical_complexity"] is True
    assert policy["creates_new_publisher"] is False
    assert policy["creates_new_orchestrator"] is False
    assert policy["auto_publish_enabled"] is False
    assert policy["auto_execution_enabled"] is False
    assert policy["operator_review_required"] is True
    assert policy["parada_atlantida_locked"] is True

def test_phase72d_page_has_single_request_box():
    page = (ROOT / "pages" / "KOS_Operator_Chat.py").read_text(encoding="utf-8-sig")
    assert "Pedido ao K-OS" in page
    assert "Pedir ao Orquestrador" in page
    assert "Detalhes técnicos" in page or "Detalhes tecnicos" in page
    assert "Você não precisa procurar funcionalidades" in page
