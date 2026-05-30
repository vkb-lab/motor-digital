from __future__ import annotations

import json

from k_atlas.core.mission_planner.planner import MissionPlanner

from .bridge import MissionExecutorBridge


if __name__ == "__main__":
    planner = MissionPlanner()
    plan = planner.build_plan({
        "title": "Missao diaria K-Atlas OS via Executor Bridge",
        "mission_type": "daily_operator",
        "objective": "validar ponte entre Mission Planner e Command Center",
        "priority": "high",
        "official_publish": False,
        "auto_publish": False,
        "auto_deploy": False,
        "mass_messaging": False,
        "browser_automation": False,
        "external_api_enabled": False,
    })

    result = MissionExecutorBridge().execute_plan(
        plan=plan,
        payload={
            "dry_run": True,
            "max_tasks": 10,
            "official_publish": False,
            "auto_publish": False,
            "auto_deploy": False,
            "mass_messaging": False,
            "browser_automation": False,
            "external_api_enabled": False,
        },
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
