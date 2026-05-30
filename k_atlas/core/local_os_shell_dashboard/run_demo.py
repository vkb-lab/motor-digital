from __future__ import annotations

import json
from .shell import LocalOSShellDashboard

if __name__ == "__main__":
    result = LocalOSShellDashboard().build_report()
    print(json.dumps(result, ensure_ascii=False, indent=2))
