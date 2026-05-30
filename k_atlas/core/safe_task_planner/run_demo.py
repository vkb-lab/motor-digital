from __future__ import annotations

import json
from .planner import SafeTaskPlanner

if __name__ == "__main__":
    result = SafeTaskPlanner().create_plan()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
