from __future__ import annotations

import json

from k_atlas.core.mission_pack_generator.generator import MissionPackGenerator

from .bridge import MissionPackBridge


if __name__ == "__main__":
    generator = MissionPackGenerator()
    generator.generate_pack(
        objective="Criar arquivo gerado pelo Mission Pack Bridge",
        target_path="reports/autoprog_generated/mission_pack_bridge_demo.md",
    )

    bridge = MissionPackBridge()
    result = bridge.bridge_latest()
    print(json.dumps(result, ensure_ascii=False, indent=2))
