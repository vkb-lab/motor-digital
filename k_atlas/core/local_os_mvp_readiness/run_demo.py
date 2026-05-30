from __future__ import annotations

import json

from .readiness import LocalOSMVPReadiness


if __name__ == "__main__":
    readiness = LocalOSMVPReadiness()
    report = readiness.build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
