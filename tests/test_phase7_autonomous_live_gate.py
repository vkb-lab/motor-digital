from k_atlas.command_autopilot_live_preview import run_live_gate_autopilot_preview

def test_live_gate_preview():
    result = run_live_gate_autopilot_preview()
    assert result["status"] == "PENDING_FINAL_APPROVAL"
    assert "live_connector_readiness" in result
    assert result["live_gate"]["status"] == "PENDING_APPROVAL"
