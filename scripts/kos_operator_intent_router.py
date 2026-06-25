from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class IntentRoute:
    intent: str
    target: str
    risk: str
    external_action: bool = False


ROUTES = [
    IntentRoute("operator_chat", "pages/KOS_Operator_Chat.py", "low"),
    IntentRoute("command_cockpit", "pages/KOS_Unified_Command_Cockpit.py", "low"),
    IntentRoute("runtime_health", "pages/KOS_Runtime_Health.py", "low"),
    IntentRoute("mission_queue", "pages/KOS_Mission_Queue.py", "low"),
    IntentRoute("human_approval", "pages/KOS_Human_Approval.py", "medium"),
    IntentRoute("render_status", "app_render.py", "low"),
    IntentRoute("gmail_status", "reports/KOS_GMAIL_REAL_CONNECTION_STATUS.md", "medium"),
    IntentRoute("unknown", "manual_review", "medium"),
]


KEYWORDS = {
    "operator_chat": ["chat", "operator", "pedido"],
    "command_cockpit": ["cockpit", "command", "comando"],
    "runtime_health": ["runtime", "health", "status"],
    "mission_queue": ["mission", "missao", "fila", "queue"],
    "human_approval": ["approval", "aprovacao", "gate", "human"],
    "render_status": ["render", "cloud", "mobile"],
    "gmail_status": ["gmail", "email", "inbox"],
}


def route_intent(text: str) -> dict:
    low = text.lower()
    route_id = "unknown"
    for intent, words in KEYWORDS.items():
        if any(word in low for word in words):
            route_id = intent
            break
    route = next(item for item in ROUTES if item.intent == route_id)
    return {
        "status": "KOS_OPERATOR_INTENT_ROUTE_READY",
        "intent": route.intent,
        "target": route.target,
        "risk": route.risk,
        "external_action": route.external_action,
        "requires_human_gate": route.risk != "low" or route.external_action,
    }


def main() -> None:
    print(json.dumps(route_intent("status"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
