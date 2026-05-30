from __future__ import annotations

import json

from .cockpit import DailyOperatorCockpit


if __name__ == "__main__":
    result = DailyOperatorCockpit().collect()
    print(json.dumps(result, ensure_ascii=False, indent=2))
