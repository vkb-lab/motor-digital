from k_atlas.kaizen.human_approval import (
    create_approval_request,
    approve_dry_run,
    reject_request,
    summarize_approvals,
    DRY_RUN_CONFIRMATION,
)

def test_create_approval_request_is_safe():
    req = create_approval_request(
        title="Teste approval",
        description="Aprovar dry-run.",
        action_type="safe_executor_bundle",
        risk_level="low",
        payload={"actions": ["git_status"]}
    )
    assert req["status"] == "pending"
    assert req["execution_allowed"] is False
    assert req["real_action_allowed"] is False
    assert req["paid_ai_allowed"] is False
    assert req["external_publish_allowed"] is False

def test_wrong_confirmation_blocks_approval():
    req = create_approval_request(
        title="Teste confirmacao errada",
        description="Nao aprovar.",
        action_type="safe_executor_bundle",
        risk_level="low"
    )
    result = approve_dry_run(req["id"], "YES")
    assert result["ok"] is False
    assert result["execution_allowed"] is False

def test_approve_dry_run_does_not_allow_execution():
    req = create_approval_request(
        title="Teste approve dry-run",
        description="Aprovar apenas dry-run.",
        action_type="safe_executor_bundle",
        risk_level="low"
    )
    result = approve_dry_run(req["id"], DRY_RUN_CONFIRMATION)
    assert result["ok"] is True
    assert result["status"] == "APPROVED_DRY_RUN_ONLY"
    assert result["execution_allowed"] is False
    assert result["real_action_allowed"] is False
    assert result["paid_ai_allowed"] is False
    assert result["external_publish_allowed"] is False

def test_reject_request_blocks_execution():
    req = create_approval_request(
        title="Teste reject",
        description="Rejeitar.",
        action_type="safe_executor_bundle",
        risk_level="low"
    )
    result = reject_request(req["id"], "teste")
    assert result["ok"] is True
    assert result["status"] == "APPROVAL_REJECTED"
    assert result["execution_allowed"] is False
