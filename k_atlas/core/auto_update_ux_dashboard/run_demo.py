from __future__ import annotations

import json

from .dashboard import AutoUpdateUXDashboard


if __name__ == "__main__":
    result = AutoUpdateUXDashboard().build_report()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
