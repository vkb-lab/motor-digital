from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class IntentRoute:
    intent: str
    target: str
    risk: str
    external_action: bool = False


ROUTES = [
    IntentRoute("adversarial_guardrail", "human_gate", "high", True),
    IntentRoute("brain_provider_status", "scripts/run_kos_brain_provider_status.py", "low"),
    IntentRoute("google_toolbelt_status", "scripts/run_google_ai_toolbelt_bridge.py", "low"),
    IntentRoute("subsidy_package", "mission_queue", "medium"),
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
    "adversarial_guardrail": [
        "ignore guardrails",
        "ignore os guardrails",
        "burlar guardrails",
        "sem human gate",
        "publique sem aprovar",
        "publique agora",
        "deleta sem perguntar",
    ],
    "brain_provider_status": [
        "qual cerebro",
        "cerebro voce esta usando",
        "brain provider",
        "modelo voce esta usando",
        "qual ia voce esta usando",
    ],
    "gmail_status": ["gmail", "email", "inbox", "conectado"],
    "google_toolbelt_status": [
        "ferramentas google",
        "google toolbelt",
        "toolbelt google",
        "google existem",
        "google voce tem",
    ],
    "subsidy_package": [
        "pacote de subsidio",
        "monte pacote de subsidio",
        "subsidio",
        "subvencao",
        "edital",
        "grant",
    ],
    "operator_chat": ["chat", "operator", "pedido"],
    "command_cockpit": ["cockpit", "command", "comando"],
    "runtime_health": ["runtime", "health", "status"],
    "mission_queue": ["mission", "missao", "fila", "queue"],
    "human_approval": ["approval", "aprovacao", "gate", "human"],
    "render_status": ["render", "cloud", "mobile"],
}


def normalize_intent_text(text: str) -> str:
    value = str(text or "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def route_intent(text: str) -> dict:
    low = normalize_intent_text(text)
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
