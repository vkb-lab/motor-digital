from __future__ import annotations

import json
from k_atlas.core.safe_task_planner.planner import SafeTaskPlanner
from .queue import SupervisedAutonomyQueue

if __name__ == "__main__":
    SafeTaskPlanner().create_plan("demo_supervised_autonomy")
    result = SupervisedAutonomyQueue().build_queue()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
