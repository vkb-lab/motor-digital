from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

NOISE_TERMS = [
    "Human Gate",
    "Safe Action",
    "Action Packet",
    "Registry READY",
    "KOS_TOOL_REGISTRY_READY",
    "KOS_CONNECTION_REGISTRY_READY",
    "KOS_TENANT_REGISTRY_READY",
    "guardrails ativos",
    "Guardrails ativos",
    "nada foi publicado",
    ".json",
]

EXTERNAL_ACTION_WORDS = [
    "publicar",
    "publique",
    "publica",
    "publicação",
    "publicacao",
    "poste",
    "postar",
    "enviar",
    "envie",
    "manda",
    "mande",
    "mandar whatsapp",
    "mandar mensagem",
    "deploy",
    "apagar",
    "excluir",
    "alterar banco",
    "comprar",
    "pagar",
]


@dataclass
class BrainResult:
    user_response: str
    technical_evidence: dict[str, Any]


def _candidate_registry_files() -> list[Path]:
    roots = [
        ROOT / "memory",
        ROOT / "local_runtime",
        ROOT / "config",
        ROOT / "data",
    ]

    patterns = [
        "*REGISTRY*.json",
        "*CAPABILITY*.json",
        "*TENANT*.json",
        "*registry*.json",
        "*capability*.json",
        "*tenant*.json",
    ]

    found: list[Path] = []

    for base in roots:
        if not base.exists():
            continue
        for pattern in patterns:
            found.extend(base.rglob(pattern))

    return sorted(set(found))


def load_registry_snapshot() -> dict[str, Any]:
    files = _candidate_registry_files()

    snapshot: dict[str, Any] = {
        "registry_files": [],
        "text": "",
    }

    chunks: list[str] = []

    for path in files[:40]:
        try:
            rel = str(path.relative_to(ROOT))
            txt = path.read_text(encoding="utf-8", errors="ignore")
            snapshot["registry_files"].append(rel)
            chunks.append(txt[:20000])
        except Exception:
            continue

    snapshot["text"] = "\n".join(chunks)
    return snapshot


def classify_intent(message: str) -> str:
    text = message.lower()

    if any(x in text for x in ["instagram", "insta", "hupmix", "publicação", "publicacao", "reel"]):
        return "instagram_operation"

    if any(x in text for x in ["email", "gmail", "caixa de entrada"]):
        return "email_operation"

    if any(x in text for x in ["download", "downloads", "arquivos baixados"]):
        return "downloads_operation"

    if any(x in text for x in ["o que você pode", "o que voce pode", "ferramentas", "capacidades", "como pode me ajudar"]):
        return "capability_status"

    if any(x in text for x in ["saas", "produto", "mvp", "sistema", "solidificar", "consolidar"]):
        return "product_or_system_solidification"

    return "general_operator_chat"


def classify_risk(message: str) -> str:
    text = message.lower()
    if any(word in text for word in EXTERNAL_ACTION_WORDS):
        return "external_action_requires_confirmation"
    return "read_only_or_local_safe"


def detect_instagram_accounts(snapshot: dict[str, Any]) -> list[str]:
    text = snapshot.get("text", "").lower()
    accounts: list[str] = []

    if "hupmix" in text:
        accounts.append("Hupmix: registrada e tratada como caso operacional Instagram.")

    if "casa_da_limpeza" in text or "casa da limpeza" in text:
        accounts.append("Casa da Limpeza: registrada em configuração local.")

    if "parada_atlantida" in text or "parada atlântida" in text or "parada atlantida" in text:
        accounts.append("Parada Atlântida: reconhecida como projeto sensível e travada para ações externas.")

    if not accounts:
        accounts.append("Não encontrei contas Instagram nomeadas nos registries locais consultados. O próximo passo é auditar o registry de conexões.")

    return accounts


def sanitize_user_response(text: str) -> str:
    lines = []

    for line in text.splitlines():
        if any(term.lower() in line.lower() for term in NOISE_TERMS):
            continue
        lines.append(line)

    clean = "\n".join(lines).strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean


def compose_user_response(message: str, intent: str, risk: str, snapshot: dict[str, Any]) -> str:
    registry_count = len(snapshot.get("registry_files", []))

    if intent == "instagram_operation":
        accounts = detect_instagram_accounts(snapshot)
        response = "Instagram tratado como operação de leitura e auditoria.\n\n"
        response += "Estado encontrado:\n"
        response += "\n".join(f"- {item}" for item in accounts)
        response += "\n\nPróximos pedidos úteis: revisar a última publicação, gerar legenda melhor, comparar as últimas postagens ou preparar uma ação para aprovação."

    elif intent == "email_operation":
        response = (
            "Vou tratar isso como auditoria de emails.\n\n"
            "A resposta ideal do K-OS deve trazer prioridades, pendências, riscos e próximos passos, sem expor bastidor técnico."
        )

    elif intent == "downloads_operation":
        response = (
            "Vou tratar isso como organização local de arquivos.\n\n"
            "A rota segura é inventariar, classificar e sugerir organização sem apagar nada automaticamente."
        )

    elif intent == "capability_status":
        response = (
            "Hoje posso operar como centro de comando do ecossistema.\n\n"
            "Posso ajudar com K-OS, agentes, campanhas, Instagram, Ki-Publica, organização de arquivos, auditoria de conexões, criação de produtos, SaaS, relatórios, checkpoints e governança.\n\n"
            f"Encontrei {registry_count} arquivos locais de capacidade, conexão ou tenant para consulta.\n\n"
            "Melhor próximo pedido: diga o projeto e a ação desejada."
        )

    elif intent == "product_or_system_solidification":
        response = (
            "Vou tratar isso como solidificação de sistema/produto.\n\n"
            "A regra agora é consolidar o que já existe, separar resposta de evidência técnica e impedir criação de módulos soltos."
        )

    else:
        response = (
            "Entendi. Vou atuar como operador do K-OS: identificar contexto, consultar memória, avaliar risco e entregar o próximo passo útil."
        )

    if risk == "external_action_requires_confirmation":
        response += "\n\nPara executar ação externa real, preciso da sua confirmação antes."

    return sanitize_user_response(response)


def answer(message: str) -> BrainResult:
    snapshot = load_registry_snapshot()
    intent = classify_intent(message)
    risk = classify_risk(message)

    user_response = compose_user_response(
        message=message,
        intent=intent,
        risk=risk,
        snapshot=snapshot,
    )

    technical_evidence = {
        "intent": intent,
        "risk": risk,
        "registry_files_found": snapshot.get("registry_files", []),
        "contract": "KOS_OPERATOR_CHAT_RESPONSE_CONTRACT_V1",
        "root_consciousness": "KOS_ORCHESTRATOR_ROOT_CONSCIOUSNESS_V1",
    }

    return BrainResult(user_response=user_response, technical_evidence=technical_evidence)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", required=True)
    parser.add_argument("--technical", action="store_true")
    args = parser.parse_args()

    result = answer(args.ask)

    print(result.user_response)

    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / "KOS_LAST_BRAIN_GATEWAY_RESULT.json"
    report_path.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if args.technical:
        print("\n--- technical_evidence ---")
        print(json.dumps(result.technical_evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

