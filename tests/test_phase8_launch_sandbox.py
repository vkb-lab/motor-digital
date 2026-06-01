from k_atlas.launch_sandbox import run_launch_sandbox
from k_atlas.launch_sandbox.launch_plan import build_launch_plan

def test_launch_plan_is_safe():
    plan = build_launch_plan("parada_atlantida", "campanha_teste")
    assert plan["status"] == "PENDING_APPROVAL"
    assert plan["real_actions_enabled"] is False
    assert plan["manual_approval_required"] is True

def test_launch_sandbox_runs_to_confirmation():
    result = run_launch_sandbox()
    assert result["status"] == "PENDING_FINAL_APPROVAL"
    assert result["real_action_executed"] is False
    assert result["confirmation"]["status"] == "PENDING_FINAL_APPROVAL"
    assert result["board"]["status"] == "LAUNCH_BOARD_READY"
