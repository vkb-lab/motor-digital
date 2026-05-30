from __future__ import annotations

import json

from .planner import MissionPlanner


if __name__ == "__main__":
    planner = MissionPlanner()
    result = planner.plan_and_enqueue({
        "title": "Missao diaria K-Atlas OS",
        "mission_type": "daily_operator",
        "objective": "manter K-Atlas operacional, gerar relatorios, validar Git, validar daemon e preparar proximas execucoes supervisionadas",
        "priority": "high",
        "official_publish": False,
        "auto_publish": False,
        "auto_deploy": False,
        "mass_messaging": False,
        "browser_automation": False,
        "external_api_enabled": False,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
