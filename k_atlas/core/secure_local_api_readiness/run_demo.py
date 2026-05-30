from __future__ import annotations

import json
from .api import SecureLocalApiReadiness

if __name__ == "__main__":
    result = SecureLocalApiReadiness().build_report({"mode": "readiness", "bind_address": "127.0.0.1"})
    print(json.dumps(result, ensure_ascii=False, indent=2))
