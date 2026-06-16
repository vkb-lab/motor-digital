from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.closed_loop import run_closed_loop, summarize_last_reports
from k_atlas.kaizen.human_approval import DRY_RUN_CONFIRMATION
import json

if __name__ == "__main__":
    result = run_closed_loop(
        title="Fase 40 Closed Loop Demo",
        description="Executar ciclo Missao -> Plano -> Aprovacao -> Executor Sandbox -> Relatorio.",
        priority="high",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=["git_branch", "git_status"],
    )

    print(json.dumps({
        "status": "PHASE40_CLOSED_LOOP_DEMO_COMPLETED",
        "loop_status": result.get("status"),
        "loop_id": result.get("loop_id"),
        "executor_ran": result.get("executor_result") is not None,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "summary": summarize_last_reports(),
    }, ensure_ascii=False, indent=2))
