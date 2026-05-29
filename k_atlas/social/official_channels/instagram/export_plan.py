from __future__ import annotations

import json
from pathlib import Path

from .governance import validate_instagram_official_payload
from .strategy import build_instagram_launch_strategy


def export_instagram_plan(output_path: str = "reports/official_channels/instagram/k_atlas_instagram_plan.json") -> dict:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    strategy = build_instagram_launch_strategy()

    validation = validate_instagram_official_payload({
        "official_publish": False,
        "auto_publish": False,
        "external_api_enabled": False,
        "mass_messaging": False,
        "browser_automation": False,
    })

    report = {
        "ok": True,
        "checkpoint": "31",
        "name": "Instagram Oficial do K-Atlas - Identidade e Plano Operacional",
        "strategy": strategy,
        "governance_validation": validation,
    }

    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(export_instagram_plan(), ensure_ascii=False, indent=2))