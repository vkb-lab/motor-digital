"""Local campaign generation engine with no external API dependency."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .events import emit_event
from .paths import CAMPAIGNS_DIR, ensure_dirs


def generate_campaign(name: str, objective: str, audience: str = "publico geral") -> dict[str, Any]:
    ensure_dirs()
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-") or "campaign"
    campaign = {
        "name": name,
        "objective": objective,
        "audience": audience,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "channels": ["streamlit", "email", "social"],
        "content_plan": [
            {"stage": "awareness", "asset": f"Mensagem inicial para {audience}: {objective}"},
            {"stage": "conversion", "asset": f"Chamada para acao da campanha {name}"},
            {"stage": "retention", "asset": "Resumo de resultados e proximos passos"},
        ],
    }
    path = CAMPAIGNS_DIR / f"{slug}.json"
    path.write_text(json.dumps(campaign, ensure_ascii=False, indent=2), encoding="utf-8")
    emit_event("campaign_generated", {"name": name, "path": str(path)})
    return campaign


def list_campaigns() -> list[Path]:
    ensure_dirs()
    return sorted(CAMPAIGNS_DIR.glob("*.json"))

