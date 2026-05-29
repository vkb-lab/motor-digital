from __future__ import annotations

from typing import Any

from .asset_plan import build_asset_plan
from .brief import CreativeBrief
from .governance import validate_creative_media_payload
from .prompt_pack import build_prompt_pack


def build_creative_media_package(brief: CreativeBrief) -> dict[str, Any]:
    payload = {
        "project_name": brief.project_name,
        "channel": brief.channel,
        "official_publish": False,
        "auto_publish": False,
        "external_api_enabled": False,
        "browser_automation": False,
        "mass_messaging": False,
    }

    validation = validate_creative_media_payload(payload)

    prompt_pack = build_prompt_pack(brief)
    asset_plan = build_asset_plan(brief)

    return {
        "ok": validation["ok"],
        "status": "ready_for_human_review" if validation["ok"] else "blocked",
        "package_type": "creative_media_package",
        "brief": brief.to_dict(),
        "governance": validation,
        "prompt_pack": prompt_pack,
        "asset_plan": asset_plan,
        "side_effects": "none",
        "external_api_used": False,
        "official_publish_allowed": False,
        "human_review_required": True,
        "next_actions": [
            "revisar brief",
            "aprovar prompt pack",
            "gerar assets manualmente ou via API futura com vault",
            "enviar assets aprovados ao Publishing Gateway",
        ],
    }