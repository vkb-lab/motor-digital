from __future__ import annotations

import json
from .monitor import AutonomyAuditMonitor

if __name__ == "__main__":
    result = AutonomyAuditMonitor().audit()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
