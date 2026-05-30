from __future__ import annotations

import json

from .matrix import ServiceReadinessMatrix


if __name__ == "__main__":
    result = ServiceReadinessMatrix().generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
