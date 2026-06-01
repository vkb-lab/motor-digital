from k_atlas.real_execution_gate import request_real_execution

def test_real_action_blocked():
    result = request_real_execution("parada_atlantida", "instagram", "publish_instagram", {})
    assert result["status"] == "PENDING_APPROVAL"
    assert result["external_call_executed"] is False
    assert result["guard"]["allowed"] is False
