from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.kaizen.human_approval import create_approval_request, approve_dry_run, summarize_approvals, DRY_RUN_CONFIRMATION
import json

if __name__ == "__main__":
    request = create_approval_request(
        title="Fase 39 Demo Approval",
        description="Registrar aprovacao humana dry-run para bundle seguro.",
        action_type="safe_executor_bundle",
        risk_level="low",
        payload={"actions": ["git_branch", "git_status"]}
    )

    approved = approve_dry_run(request["id"], DRY_RUN_CONFIRMATION)

    print(json.dumps({
        "status": "PHASE39_HUMAN_APPROVAL_DEMO_COMPLETED",
        "approval_id": request["id"],
        "approval_status": approved.get("status"),
        "execution_allowed": False,
        "summary": summarize_approvals(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
