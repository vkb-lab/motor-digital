from __future__ import annotations

from typing import Any

from .brief import CreativeBrief


def build_asset_plan(brief: CreativeBrief) -> dict[str, Any]:
    return {
        "project_name": brief.project_name,
        "status": "planned",
        "assets": [
            {
                "asset_id": "brand_hero_image",
                "type": "image",
                "format": "16:9",
                "use": "landing_page_hero",
                "approval_required": True,
            },
            {
                "asset_id": "instagram_reel_01",
                "type": "video",
                "format": "9:16",
                "duration": "8-15s",
                "use": "instagram_reel",
                "approval_required": True,
            },
            {
                "asset_id": "carousel_manifesto",
                "type": "carousel",
                "format": "1080x1350",
                "cards": 5,
                "use": "instagram_feed",
                "approval_required": True,
            },
            {
                "asset_id": "story_proof_of_work",
                "type": "story",
                "format": "9:16",
                "use": "bastidor_operacional",
                "approval_required": True,
            },
            {
                "asset_id": "system_diagram_simple",
                "type": "diagram",
                "format": "square",
                "use": "educational_content",
                "approval_required": True,
            },
        ],
        "production_order": [
            "brand_hero_image",
            "system_diagram_simple",
            "carousel_manifesto",
            "instagram_reel_01",
            "story_proof_of_work",
        ],
    }