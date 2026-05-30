from __future__ import annotations

import json

from .dashboard import AutoprogrammingCycleDashboard


if __name__ == "__main__":
    dashboard = AutoprogrammingCycleDashboard()
    report = dashboard.build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
