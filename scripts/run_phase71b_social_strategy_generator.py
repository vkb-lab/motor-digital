from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "local_runtime" / "kos_social_ops" / "strategies"
LATEST = ROOT / "local_runtime" / "kos_social_ops" / "latest_social_strategy.json"

BLOCKED_TARGETS = {
    "paradaatlantida",
    "parada_atlantida",
    "17841480166187766",
    "869334472930140",
}

ALLOWED_TARGETS = {"hupmix"}

DEFAULT_PILLARS = [
    "bastidores",
    "produto",
    "prova_social",
    "educacao",
    "chamada_para_acao",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = value.strip("-")
    return value[:100] or "social-strategy"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def validate_target(target: str) -> dict[str, Any]:
    normalized = target.strip().lower()

    if normalized in BLOCKED_TARGETS:
        return {
            "ok": False,
            "reason": "blocked_target",
            "target": target,
        }

    if normalized not in ALLOWED_TARGETS:
        return {
            "ok": False,
            "reason": "target_not_allowed_for_phase_71b",
            "target": target,
            "allowed_targets": sorted(ALLOWED_TARGETS),
        }

    return {
        "ok": True,
        "target": normalized,
    }


def build_post_plan(objective: str, tone: str) -> list[dict[str, Any]]:
    return [
        {
            "day": 1,
            "pillar": "bastidores",
            "format": "reel_or_story",
            "idea": "mostrar bastidor simples e humano da operação",
            "caption_draft": f"{objective}. Hoje por dentro do processo, sem exagero e com clareza.",
            "cta": "acompanhe os proximos passos",
            "risk_level": "low",
        },
        {
            "day": 2,
            "pillar": "produto",
            "format": "feed",
            "idea": "explicar uma vantagem objetiva do produto ou serviço",
            "caption_draft": f"{objective}. Um ponto simples que melhora a experiencia de quem acompanha.",
            "cta": "salve para consultar depois",
            "risk_level": "low",
        },
        {
            "day": 3,
            "pillar": "educacao",
            "format": "carrossel",
            "idea": "ensinar algo util em poucos passos",
            "caption_draft": "Conteudo direto, pratico e sem promessa exagerada.",
            "cta": "envie para alguem que precisa disso",
            "risk_level": "low",
        },
        {
            "day": 4,
            "pillar": "prova_social",
            "format": "story",
            "idea": "mostrar validacao, feedback ou sinal de confianca",
            "caption_draft": "Pequenos sinais tambem mostram evolucao.",
            "cta": "responda com sua duvida",
            "risk_level": "medium",
        },
        {
            "day": 5,
            "pillar": "chamada_para_acao",
            "format": "feed_or_reel",
            "idea": "convite leve para proxima acao",
            "caption_draft": "Estamos organizando os proximos passos. Acompanhe de perto.",
            "cta": "chame no direct",
            "risk_level": "low",
        },
    ]


def build_strategy(
    target: str,
    objective: str,
    tone: str,
    campaign: str,
    strategy_id: str = "",
) -> dict[str, Any]:
    validation = validate_target(target)

    if not validation["ok"]:
        return {
            "status": "KOS_SOCIAL_STRATEGY_BLOCKED",
            "phase": "71B",
            "target": target,
            "reason": validation["reason"],
            "auto_publish_enabled": False,
            "auto_execution_enabled": False,
            "operator_review_required": True,
            "instagram_publish_executed": False,
            "real_action_executed": False,
            "created_at": now_iso(),
        }

    normalized_target = validation["target"]
    strategy_id = slug(strategy_id or f"{normalized_target}-{campaign}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

    payload = {
        "status": "KOS_SOCIAL_STRATEGY_READY",
        "phase": "71B",
        "strategy_id": strategy_id,
        "target": normalized_target,
        "campaign": campaign,
        "objective": objective,
        "tone": tone,
        "content_pillars": DEFAULT_PILLARS,
        "publish_mode": "draft_or_dry_run_first",
        "requires_human_approval": True,
        "risk_level": "low",
        "post_plan": build_post_plan(objective=objective, tone=tone),
        "audit": {
            "parada_atlantida_locked": True,
            "target_hupmix_only": True,
            "auto_publish_enabled": False,
            "auto_execution_enabled": False,
            "operator_review_required": True,
            "paid_ai_locked": True,
            "browser_scraping_enabled": False,
            "browser_logged_account_automation_used": False,
            "instagram_publish_executed": False,
            "real_action_executed": False,
        },
        "created_at": now_iso(),
    }

    payload["strategy_sha256"] = sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{strategy_id}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    LATEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    payload["path"] = str(path)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="hupmix")
    parser.add_argument("--objective", default="validar estrategia social segura para Hupmix")
    parser.add_argument("--tone", default="direto, humano e comercial sem exagero")
    parser.add_argument("--campaign", default="hupmix-test-campaign")
    parser.add_argument("--strategy-id", default="")
    args = parser.parse_args()

    result = build_strategy(
        target=args.target,
        objective=args.objective,
        tone=args.tone,
        campaign=args.campaign,
        strategy_id=args.strategy_id,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
