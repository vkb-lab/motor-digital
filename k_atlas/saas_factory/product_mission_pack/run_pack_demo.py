from __future__ import annotations

import json

from .pack import SaasProductMissionPack


if __name__ == "__main__":
    result = SaasProductMissionPack().generate(enqueue_mission=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
