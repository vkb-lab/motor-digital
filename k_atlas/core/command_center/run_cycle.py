from __future__ import annotations

import json
from .center import CommandCenter

if __name__ == "__main__":
    center = CommandCenter()
    created = center.create_cycle("ciclo autonomo supervisionado K-Atlas")
    executed = center.run_pending_once(limit=10)
    print(json.dumps({"created": created, "executed": executed}, ensure_ascii=False, indent=2))
