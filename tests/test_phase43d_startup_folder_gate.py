from k_atlas.kaizen.startup_folder_gate import build_startup_plan, check_startup_status, CONFIRMATION

def test_startup_plan_requires_confirmation():
    plan = build_startup_plan()

    assert plan["status"] == "STARTUP_FOLDER_GATE_READY"
    assert plan["confirmation_required"] == CONFIRMATION
    assert plan["requires_admin"] is False
    assert plan["registers_without_confirmation"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_startup_status_check_is_read_only():
    status = check_startup_status()

    assert status["status"] == "STARTUP_FOLDER_STATUS_CHECKED"
    assert status["real_action_executed"] is False
    assert status["paid_ai_call_executed"] is False
    assert status["instagram_publish_executed"] is False
