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
    assert "consulta registry" in page
    assert "confirmar, alterar ou cancelar por texto" in page
    assert "### Evidencia" in page
    assert "parse_text_decision" in page
    assert "register_text_decision" in page

def test_phase72d_capability_status_intent_reads_real_registries():
    page = (ROOT / "pages" / "KOS_Operator_Chat.py").read_text(encoding="utf-8-sig")
    assert "is_kos_capability_status_question" in page
    assert "KOS_TOOL_REGISTRY.json" in page
    assert "KOS_CONNECTION_REGISTRY.json" in page
    assert "KOS_PRODUCT_CAPABILITY_PACKS.json" in page
    assert "KOS_TENANT_REGISTRY.json" in page
    assert "Criar SaaS/produtos" in page
    assert "Ki-Publica/social/campanhas" in page
    assert "Conexões Google/Meta/Supabase/Git/Render" in page
    assert "Autonomia/agentes/runtime" in page
    assert "Segurança/Human Gate" in page
    assert "O que posso acionar agora" in page
    assert "Coworker operacional supervisionado" in page
