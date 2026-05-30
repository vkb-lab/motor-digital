from __future__ import annotations

import json

from .queue import OperatorMissionQueue


if __name__ == "__main__":
    queue = OperatorMissionQueue()
    mission = queue.enqueue()
    approval = queue.approve(
        mission_id=mission["mission_id"],
        reviewer="k_atlas_operator",
        notes="Aprovado para planejamento. Sem execucao real.",
    )
    export = queue.export_command_center_tasks(mission["mission_id"])
    report = queue.save_report()
    print(json.dumps({"mission": mission, "approval": approval, "export": export, "report": report}, ensure_ascii=False, indent=2))
