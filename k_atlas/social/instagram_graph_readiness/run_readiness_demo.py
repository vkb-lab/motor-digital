from __future__ import annotations

import json

from .readiness import InstagramGraphReadiness


if __name__ == "__main__":
    result = InstagramGraphReadiness().generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
