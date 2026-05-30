from __future__ import annotations

import json

from .capsule import LocalOSReleaseCapsule


if __name__ == "__main__":
    capsule = LocalOSReleaseCapsule()
    report = capsule.build_capsule()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
