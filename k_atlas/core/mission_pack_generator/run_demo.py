from __future__ import annotations

import json

from .generator import MissionPackGenerator


if __name__ == "__main__":
    generator = MissionPackGenerator()
    report = generator.generate_pack(
        objective="Criar relatorio demo do Mission Pack Generator",
        target_path="reports/autoprog_generated/mission_pack_generator_demo.md",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
