from __future__ import annotations

import json

from .rollback import ManualApplyRollbackExecutor


if __name__ == "__main__":
    executor = ManualApplyRollbackExecutor()
    result = executor.dry_run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
