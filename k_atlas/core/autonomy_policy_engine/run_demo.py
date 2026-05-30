from __future__ import annotations

import json
from .policy import AutonomyPolicyEngine

if __name__ == "__main__":
    result = AutonomyPolicyEngine().evaluate({"mode": "recommend", "risk_level": "low"})
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
