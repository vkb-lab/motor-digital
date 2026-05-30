from __future__ import annotations

import json

from k_atlas.core.command_center_mission_intake.intake import CommandCenterMissionIntake
from k_atlas.core.operator_mission_queue.queue import OperatorMissionQueue

from .runner import CommandCenterPlanningRunner


if __name__ == "__main__":
    operator_queue = OperatorMissionQueue()
    mission = operator_queue.enqueue()
    operator_queue.approve(
        mission_id=mission["mission_id"],
        reviewer="k_atlas_operator",
        notes="Aprovado para planejamento Command Center. Sem execução real.",
    )
    operator_queue.export_command_center_tasks(mission["mission_id"])

    intake = CommandCenterMissionIntake()
    intake.process_exports()

    runner = CommandCenterPlanningRunner()
    result = runner.run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
