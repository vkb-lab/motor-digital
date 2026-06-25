from __future__ import annotations

from scripts.kos_operator_intent_router import route_intent


def test_operator_intent_router_routes_known_intents():
    assert route_intent("abrir operator chat")["intent"] == "operator_chat"
    assert route_intent("ver runtime health")["intent"] == "runtime_health"
    assert route_intent("status gmail")["intent"] == "gmail_status"


def test_operator_intent_router_is_isolated_and_safe():
    result = route_intent("publicar campanha agora")
    assert result["status"] == "KOS_OPERATOR_INTENT_ROUTE_READY"
    assert result["external_action"] is False
    assert result["target"] == "manual_review"
