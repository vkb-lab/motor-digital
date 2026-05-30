from __future__ import annotations

import json

from k_atlas.core.local_action_contracts.contracts import LocalActionContractRegistry
from k_atlas.core.local_action_router.router import LocalActionRouter
from k_atlas.core.local_execution_queue.queue import LocalExecutionQueue
from .dashboard import AssistedExecutionDashboard


if __name__ == "__main__":
    LocalActionContractRegistry().build_contracts()
    LocalActionRouter().route({
        "action_type": "run_mission_pipeline",
        "human_approved": True,
        "auto_execute": False,
        "real_execution_enabled": False,
        "external_api_enabled": False,
        "auto_publish": False,
        "auto_send": False,
        "auto_deploy": False,
        "browser_automation": False,
        "mouse_automation": False,
        "remote_control_enabled": False,
    })
    LocalExecutionQueue().enqueue_latest_ready_route()
    result = AssistedExecutionDashboard().build_report()
    print(json.dumps(result, ensure_ascii=False, indent=2))
