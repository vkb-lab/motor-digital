from __future__ import annotations

import json

from .pack import SocialGrowthMissionPack


if __name__ == "__main__":
    result = SocialGrowthMissionPack().generate(enqueue_mission=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
