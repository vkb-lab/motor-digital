from __future__ import annotations

import json

from k_atlas.core.update_intake_queue.queue import UpdateIntakeQueue
from k_atlas.core.update_verification_gate.gate import UpdateVerificationGate
from k_atlas.core.update_apply_runner.runner import UpdateApplyRunner
from k_atlas.core.update_rollback_hook.hook import UpdateRollbackHook
from k_atlas.core.update_pipeline_dashboard.dashboard import UpdatePipelineDashboard


if __name__ == "__main__":
    intake = UpdateIntakeQueue()
    intake.enqueue({
        "source": "demo",
        "installer_name": "K_ATLAS_BATCH_DEMO_UPDATE.ps1",
    })
    intake.build_report()

    gate = UpdateVerificationGate()
    gate.build_verified_queue()

    runner = UpdateApplyRunner()
    runner.record_supervised_apply_ready()

    hook = UpdateRollbackHook()
    hook.create_hook("demo_update_pipeline")

    dashboard = UpdatePipelineDashboard()
    print(json.dumps(dashboard.build_report(), ensure_ascii=False, indent=2))
