from k_atlas.command_autopilot import run_autopilot_demo

def test_final_approval_pending():
    result = run_autopilot_demo()
    review = result["final_review"]
    assert review["status"] == "PENDING_APPROVAL"
    assert review["manual_approval_required"] is True
    assert review["real_actions_blocked"] is True
