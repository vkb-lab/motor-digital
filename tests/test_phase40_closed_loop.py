from k_atlas.kaizen.closed_loop import run_closed_loop
from k_atlas.kaizen.human_approval import DRY_RUN_CONFIRMATION

def test_closed_loop_without_confirmation_waits():
    result = run_closed_loop(
        title="Teste sem aprovacao",
        description="Deve aguardar aprovacao humana.",
        priority="high",
        typed_confirmation="",
        safe_actions=["git_branch"],
    )

    assert result["status"] == "CLOSED_LOOP_WAITING_APPROVAL"
    assert result["executor_result"] is None
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False

def test_closed_loop_with_confirmation_runs_only_safe_executor():
    result = run_closed_loop(
        title="Teste com aprovacao dry-run",
        description="Deve rodar apenas safe executor allowlist.",
        priority="high",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=["git_branch"],
    )

    assert result["status"] == "CLOSED_LOOP_SANDBOX_COMPLETED"
    assert result["executor_result"] is not None
    assert result["executor_result"]["real_action_executed"] is False
    assert result["executor_result"]["paid_ai_call_executed"] is False
    assert result["executor_result"]["instagram_publish_executed"] is False

def test_closed_loop_blocks_unknown_action_via_safe_executor():
    result = run_closed_loop(
        title="Teste acao bloqueada",
        description="Safe executor deve bloquear acao fora da allowlist.",
        priority="medium",
        typed_confirmation=DRY_RUN_CONFIRMATION,
        safe_actions=["instagram_publish"],
    )

    assert result["executor_result"] is not None
    assert result["executor_result"]["ok"] is False
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
