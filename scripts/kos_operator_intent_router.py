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
    IntentRoute("origin_core_status", "scripts/run_kos_origin_core_status.py", "low"),
    IntentRoute("brain_provider_status", "scripts/run_kos_brain_provider_status.py", "low"),
    IntentRoute("google_toolbelt_status", "scripts/run_google_ai_toolbelt_bridge.py", "low"),
    IntentRoute("work_sequence_list", "scripts/run_kos_work_sequence.py", "low"),
    IntentRoute("work_sequence_plan", "scripts/run_kos_work_sequence.py", "low"),
    IntentRoute("navigation_status", "scripts/run_kos_navigation_status.py", "low"),
    IntentRoute("personal_data_estate_status", "scripts/run_personal_data_estate_status.py", "low"),
    IntentRoute("local_storage_status", "scripts/run_local_storage_estate_status.py", "low"),
    IntentRoute("render_readiness_status", "scripts/run_render_deploy_readiness_status.py", "low"),
    IntentRoute("subsidy_package", "mission_queue", "medium"),
    IntentRoute("gmail_modify_blocked", "human_gate", "high", True),
    IntentRoute("gmail_audit", "scripts/run_gmail_operator.py", "low"),
    IntentRoute("gmail_digest", "scripts/run_gmail_operator.py", "low"),
    IntentRoute("operator_chat", "pages/KOS_Operator_Chat.py", "low"),
    IntentRoute("command_cockpit", "pages/KOS_Unified_Command_Cockpit.py", "low"),
    IntentRoute("runtime_health", "pages/KOS_Runtime_Health.py", "low"),
    IntentRoute("mission_queue", "pages/KOS_Mission_Queue.py", "low"),
    IntentRoute("human_approval", "pages/KOS_Human_Approval.py", "medium"),
    IntentRoute("render_status", "app_render.py", "low"),
    IntentRoute("gmail_status", "scripts/run_gmail_operator.py", "low"),
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
    "gmail_modify_blocked": [
        "apague email",
        "apague emails",
        "delete email",
        "delete emails",
        "deletar email",
        "deletar emails",
        "arquivar email",
        "arquive email",
        "marcar email como lido",
        "mover email",
        "envie email",
        "mandar email",
        "responda email",
        "responder email",
        "reply email",
    ],
    "brain_provider_status": [
        "qual cerebro",
        "cerebro voce esta usando",
        "brain provider",
        "modelo voce esta usando",
        "qual ia voce esta usando",
    ],
    "origin_core_status": [
        "origin core",
        "nucleo de origem",
        "fonte de verdade",
        "essencia do k-os",
        "essência do k-os",
    ],
    "gmail_audit": [
        "audite meus emails",
        "auditar meus emails",
        "emails recentes",
        "relatorio gmail",
        "relatorio de emails",
    ],
    "gmail_digest": [
        "verifique meu email",
        "cheque meu email",
        "tem email novo",
        "veja meus emails",
        "resuma minha caixa",
        "o que chegou no gmail",
    ],
    "gmail_status": [
        "gmail esta conectado",
        "gmail está conectado",
        "gmail conectado",
        "status gmail",
        "status do gmail",
    ],
    "google_toolbelt_status": [
        "ferramentas google",
        "google toolbelt",
        "toolbelt google",
        "google existem",
        "google voce tem",
    ],
    "work_sequence_list": [
        "listar sequencias",
        "sequencias de trabalho",
        "work sequence list",
        "listar work sequences",
    ],
    "work_sequence_plan": [
        "plano personal_data_foundation",
        "planejar personal_data_foundation",
        "work sequence plan",
        "plano da sequencia",
    ],
    "navigation_status": [
        "navigation status",
        "status navegacao",
        "navegacao customizada",
        "custom navigation",
    ],
    "personal_data_estate_status": [
        "personal data estate",
        "dados pessoais status",
        "status dados pessoais",
    ],
    "local_storage_status": [
        "local storage status",
        "armazenamento local status",
        "status storage local",
    ],
    "render_readiness_status": [
        "render readiness",
        "readiness render",
        "pronto para render",
        "status deploy render",
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
    payload = {
        "status": "KOS_OPERATOR_INTENT_ROUTE_READY",
        "intent": route.intent,
        "target": route.target,
        "risk": route.risk,
        "external_action": route.external_action,
        "requires_human_gate": route.risk != "low" or route.external_action,
    }
    readonly_commands = {
        "origin_core_status": "python scripts/run_kos_origin_core_status.py --mode status",
        "brain_provider_status": "python scripts/run_kos_brain_provider_status.py --mode status",
        "google_toolbelt_status": "python scripts/run_google_ai_toolbelt_bridge.py --mode audit",
        "work_sequence_list": "python scripts/run_kos_work_sequence.py --mode list",
        "work_sequence_plan": "python scripts/run_kos_work_sequence.py --mode plan --sequence personal_data_foundation",
        "navigation_status": "python scripts/run_kos_navigation_status.py --mode status",
        "personal_data_estate_status": "python scripts/run_personal_data_estate_status.py --mode status",
        "local_storage_status": "python scripts/run_local_storage_estate_status.py --mode status",
        "render_readiness_status": "python scripts/run_render_deploy_readiness_status.py --mode status",
    }
    if route.intent in readonly_commands:
        payload.update({
            "action_allowed": True,
            "execution_mode": "local_readonly",
            "suggested_command": readonly_commands[route.intent],
        })
    if route.intent == "gmail_status":
        payload.update({
            "action_allowed": True,
            "execution_mode": "local_readonly",
            "suggested_command": "python scripts/run_gmail_operator.py --mode status --profile rogger",
        })
    elif route.intent == "gmail_audit":
        payload.update({
            "action_allowed": True,
            "execution_mode": "local_readonly",
            "suggested_command": 'python scripts/run_gmail_operator.py --mode report --profile rogger --query "newer_than:7d" --max-results 20',
        })
    elif route.intent == "gmail_digest":
        payload.update({
            "action_allowed": True,
            "execution_mode": "local_readonly",
            "suggested_command": 'python scripts/run_gmail_operator.py --mode report --profile rogger --query "newer_than:7d" --max-results 30',
        })
    elif route.intent == "gmail_modify_blocked":
        payload.update({
            "action_allowed": False,
            "requires_human_gate": True,
            "reason": "modifying Gmail is blocked unless explicitly approved",
        })
    return payload


def main() -> None:
    print(json.dumps(route_intent("status"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
