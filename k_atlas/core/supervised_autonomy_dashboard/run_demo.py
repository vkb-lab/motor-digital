from __future__ import annotations

import json
from k_atlas.core.safe_task_planner.planner import SafeTaskPlanner
from k_atlas.core.supervised_autonomy_queue.queue import SupervisedAutonomyQueue
from .dashboard import SupervisedAutonomyDashboard

if __name__ == "__main__":
    SafeTaskPlanner().create_plan("demo_supervised_autonomy_dashboard")
    SupervisedAutonomyQueue().build_queue()
    result = SupervisedAutonomyDashboard().build_report()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
