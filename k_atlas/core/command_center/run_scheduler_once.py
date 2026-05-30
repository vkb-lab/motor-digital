from __future__ import annotations

import json

from .scheduler import CommandCenterScheduler


if __name__ == "__main__":
    result = CommandCenterScheduler().run_once(
        objective="teste operacional do scheduler do Command Center",
        execute_tasks=True,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
