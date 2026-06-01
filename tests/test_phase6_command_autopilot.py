from k_atlas.command_autopilot import run_autopilot_demo

def test_autopilot_demo_result():
    result = run_autopilot_demo()
    assert result["client_id"] == "parada_atlantida"
    assert result["status"] == "PENDING_FINAL_APPROVAL"
    assert result["final_review"]["status"] == "PENDING_APPROVAL"
