from k_atlas.safe_execution import run_approved_safe_execution
from k_atlas.safe_execution.channel_queue import build_channel_queue

def test_queue_is_safe():
    queue = build_channel_queue("parada_atlantida", "campanha_teste")
    assert queue["status"] == "QUEUE_READY"
    assert queue["real_actions_enabled"] is False
    assert len(queue["items"]) >= 5

def test_safe_execution_runs_without_real_action():
    result = run_approved_safe_execution()
    assert result["status"] == "SAFE_EXECUTION_COMPLETED"
    assert result["real_action_executed"] is False
    assert result["external_call_executed"] is False
    assert result["review"]["status"] == "SAFE_EXECUTION_REVIEW_READY"
