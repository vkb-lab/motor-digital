from __future__ import annotations

import json
from .lan import LANCockpitAccess

if __name__ == "__main__":
    result = LANCockpitAccess().build_plan({"mode": "readiness", "port": 8506})
    print(json.dumps(result, ensure_ascii=False, indent=2))
