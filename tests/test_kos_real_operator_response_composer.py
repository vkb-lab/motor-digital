from scripts.kos_real_operator_response_composer import compose_for_chat


def test_extracts_real_answer_and_hides_technical_noise():
    raw = """
Resposta do K-OS
Entendi
quais instagram estão conectados

O que posso acionar agora
Meta Graph read-only
Safe Action / Human Gate

Rascunho operacional
Pronto para revisão
Resposta direta
Instagram conectado operacionalmente agora: Hupmix.
Contas sociais registradas no K-OS
Casa da Limpeza | target=casa_da_limpeza | status=active_local_config | publish bloqueado
Hupmix | target=hupmix | status=active_case_school | publish bloqueado
Parada Atlantida | target=parada_atlantida | status=locked | publish bloqueado
Seguranca
Token Meta/Instagram nao foi impresso.
Guardrails ativos: sem publicacao automatica.
"""

    result = compose_for_chat(raw)
    main = result["user_response"]

    assert "Instagram conectado agora: Hupmix" in main
    assert "Casa da Limpeza" in main
    assert "Parada" in main
    assert "Hupmix" in main
    assert "Conta" in main or "@hupmix" in main
    assert "Posso revisar" in main or "revisar" in main.lower()
    assert "O que posso acionar agora" not in main
    assert "Safe Action" not in main
    assert "Human Gate" not in main
    assert "Guardrails ativos" not in main
    assert "Token Meta" not in main
    assert "target=" not in main
    assert "status=" not in main
    assert "provider=" not in main
    assert "risco=" not in main
    assert "returncode=" not in main
    assert "publish bloqueado" not in main

