from __future__ import annotations

import json

from k_atlas.core.operator_mission_queue.queue import OperatorMissionQueue

from .intake import CommandCenterMissionIntake


if __name__ == "__main__":
    operator_queue = OperatorMissionQueue()
    mission = operator_queue.enqueue()
    operator_queue.approve(
        mission_id=mission["mission_id"],
        reviewer="k_atlas_operator",
        notes="Aprovado para Command Center Intake. Sem execução real.",
    )
    operator_queue.export_command_center_tasks(mission["mission_id"])

    intake = CommandCenterMissionIntake()
    result = intake.process_exports()
    print(json.dumps(result, ensure_ascii=False, indent=2))
