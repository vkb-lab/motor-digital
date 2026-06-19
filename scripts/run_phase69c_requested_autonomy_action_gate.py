from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ACTION_REGISTRY = {
    "email_watch": {
        "category": "observe",
        "default_permission": "draft_only",
        "requires_connector": True,
        "requires_human_approval": False,
        "can_send_external_message": False,
        "description": "Monitorar emails autorizados e gerar resumo/triagem. Nao responde sozinho.",
    },
    "email_reply_draft": {
        "category": "draft",
        "default_permission": "draft_only",
        "requires_connector": True,
        "requires_human_approval": True,
        "can_send_external_message": False,
        "description": "Criar rascunho de resposta. Envio real exige confirmacao humana.",
    },
    "campaign_continue": {
        "category": "campaign",
        "default_permission": "prepare_only",
        "requires_connector": False,
        "requires_human_approval": False,
        "can_send_external_message": False,
        "description": "Dar sequencia operacional a campanha: checklist, proximo conteudo, relatorio e fila.",
    },
    "campaign_publish_prepare": {
        "category": "publish",
        "default_permission": "prepare_only",
        "requires_connector": False,
        "requires_human_approval": True,
        "can_send_external_message": False,
        "description": "Preparar publicacao, legenda, assets e auditoria. Nao publica sozinho.",
    },
    "instagram_publish": {
        "category": "external_publish",
        "default_permission": "human_confirmed_only",
        "requires_connector": True,
        "requires_human_approval": True,
        "can_send_external_message": True,
        "description": "Publicacao externa real. Sempre exige confirmacao humana e flags reais.",
    },
    "product_launch_prepare": {
        "category": "launch",
        "default_permission": "prepare_only",
        "requires_connector": False,
        "requires_human_approval": False,
        "can_send_external_message": False,
        "description": "Preparar checklist de lancamento, pagina, copy, QA e plano.",
    },
    "product_launch_execute": {
        "category": "launch",
        "default_permission": "human_confirmed_only",
        "requires_connector": True,
        "requires_human_approval": True,
        "can_send_external_message": True,
        "description": "Lancamento externo real. Sempre exige confirmacao humana.",
    },
    "deploy_prepare": {
        "category": "deploy",
        "default_permission": "prepare_only",
        "requires_connector": False,
        "requires_human_approval": False,
        "can_send_external_message": False,
        "description": "Preparar deploy, checklist, relatorio e comandos. Nao executa deploy sozinho.",
    },
    "deploy_execute": {
        "category": "deploy",
        "default_permission": "human_confirmed_only",
        "requires_connector": True,
        "requires_human_approval": True,
        "can_send_external_message": True,
        "description": "Deploy real. Exige confirmacao humana.",
    },
    "github_commit_push": {
        "category": "repo",
        "default_permission": "system_confirmed_safe",
        "requires_connector": False,
        "requires_human_approval": False,
        "can_send_external_message": False,
        "description": "Commit/push de fases geradas pelo K-OS com testes e Git limpo.",
    },
}

PERMISSION_LEVELS = {
    "blocked": {
        "rank": 0,
        "description": "Sempre bloqueado.",
    },
    "observe_only": {
        "rank": 1,
        "description": "Pode ler fonte autorizada e gerar resumo local.",
    },
    "draft_only": {
        "rank": 2,
        "description": "Pode criar rascunho, sem envio externo.",
    },
    "prepare_only": {
        "rank": 3,
        "description": "Pode preparar plano, checklist, assets e fila local.",
    },
    "system_confirmed_safe": {
        "rank": 4,
        "description": "Pode executar acao local segura, auditada e reversivel.",
    },
    "human_confirmed_only": {
        "rank": 5,
        "description": "So executa com confirmacao humana explicita.",
    },
}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def validate_request(action: str, requested_permission: str = "prepare_only", human_confirmed: bool = False) -> dict[str, Any]:
    if action not in ACTION_REGISTRY:
        return {
            "status": "KOS_REQUESTED_AUTONOMY_ACTION_BLOCKED",
            "reason": "unknown_action",
            "action": action,
            "requested_permission": requested_permission,
            "allowed": False,
        }

    spec = ACTION_REGISTRY[action]
    default_permission = spec["default_permission"]

    requested_rank = PERMISSION_LEVELS.get(requested_permission, {"rank": -1})["rank"]
    default_rank = PERMISSION_LEVELS.get(default_permission, {"rank": -1})["rank"]

    requires_human = bool(spec["requires_human_approval"])
    external = bool(spec["can_send_external_message"])

    if requested_permission == "blocked":
        allowed = False
        reason = "requested_permission_blocked"
    elif requested_rank < 0:
        allowed = False
        reason = "unknown_permission"
    elif default_permission == "human_confirmed_only" and not human_confirmed:
        allowed = False
        reason = "human_confirmation_required"
    elif external and not human_confirmed:
        allowed = False
        reason = "external_action_requires_human_confirmation"
    elif requested_rank > default_rank and not human_confirmed:
        allowed = False
        reason = "requested_permission_exceeds_default_gate"
    else:
        allowed = True
        reason = "allowed_by_requested_autonomy_gate"

    return {
        "status": "KOS_REQUESTED_AUTONOMY_ACTION_ALLOWED" if allowed else "KOS_REQUESTED_AUTONOMY_ACTION_BLOCKED",
        "action": action,
        "category": spec["category"],
        "requested_permission": requested_permission,
        "default_permission": default_permission,
        "requires_connector": spec["requires_connector"],
        "requires_human_approval": requires_human,
        "can_send_external_message": external,
        "human_confirmed": human_confirmed,
        "allowed": allowed,
        "reason": reason,
        "description": spec["description"],
        "production_publish_locked": True,
        "paid_ai_locked": True,
        "instagram_publish_executed": False,
        "browser_logged_account_automation_used": False,
        "created_at": now_iso(),
    }

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--action", default="campaign_continue")
    parser.add_argument("--permission", default="prepare_only")
    parser.add_argument("--human-confirmed", action="store_true")
    args = parser.parse_args()

    result = validate_request(args.action, args.permission, args.human_confirmed)

    out = ROOT / "local_runtime" / "kos_requested_autonomy" / "latest_action_gate_validation.json"
    write_json(out, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] in {
        "KOS_REQUESTED_AUTONOMY_ACTION_ALLOWED",
        "KOS_REQUESTED_AUTONOMY_ACTION_BLOCKED",
    } else 1

if __name__ == "__main__":
    raise SystemExit(main())
