from __future__ import annotations

import json

from .dashboard import SecureLocalApiDashboard


if __name__ == "__main__":
    dashboard = SecureLocalApiDashboard()
    print(json.dumps(dashboard.build_report(), ensure_ascii=False, indent=2, sort_keys=True))
