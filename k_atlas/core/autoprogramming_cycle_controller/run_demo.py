from __future__ import annotations
import json
from .controller import AutoprogrammingCycleController

if __name__ == "__main__":
    print(json.dumps(AutoprogrammingCycleController().build_decision({"mode": "recommend"}), ensure_ascii=False, indent=2))
