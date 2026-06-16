from k_atlas.kaizen.windows_task_gate import build_registration_plan, check_windows_task_status, CONFIRMATION

def test_registration_plan_requires_exact_confirmation():
    plan = build_registration_plan()

    assert plan["status"] == "WINDOWS_TASK_REGISTRATION_GATE_READY"
    assert plan["confirmation_required"] == CONFIRMATION
    assert plan["registers_without_confirmation"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_status_check_is_read_only():
    status = check_windows_task_status()

    assert status["status"] == "WINDOWS_TASK_STATUS_CHECKED"
    assert status["real_action_executed"] is False
    assert status["paid_ai_call_executed"] is False
    assert status["instagram_publish_executed"] is False
