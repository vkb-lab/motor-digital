from __future__ import annotations

import json

from .brain import LocalOSBrainGovernance


if __name__ == "__main__":
    brain = LocalOSBrainGovernance()

    requests = [
        {
            "agent": "mission_generator",
            "action": "create_local_mission",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
        },
        {
            "agent": "execution_agent",
            "action": "apply_local_change",
            "human_approved": False,
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
        },
        {
            "agent": "remote_assist_agent",
            "action": "control_mouse",
            "auto_execute": False,
            "real_execution_enabled": False,
            "external_api_enabled": False,
        },
    ]

    results = []
    for request in requests:
        decision = brain.decide(request)
        feedback = brain.route_feedback(decision)
        results.append({"decision": decision, "feedback": feedback})

    report = brain.build_report()
    print(json.dumps({"results": results, "report": report}, ensure_ascii=False, indent=2))
