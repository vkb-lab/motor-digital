from k_atlas.kaizen.runtime_control import build_runtime_control_status, check_runtime_processes

def test_runtime_control_status_is_safe():
    status = build_runtime_control_status()

    assert status["status"] == "KOS_RUNTIME_CONTROL_STATUS_READY"
    assert status["real_action_executed"] is False
    assert status["paid_ai_call_executed"] is False
    assert status["instagram_publish_executed"] is False
    assert status["external_side_effects_executed"] is False

def test_runtime_process_check_is_read_only():
    result = check_runtime_processes()

    assert result["status"] == "RUNTIME_PROCESS_CHECKED"
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False

def test_runtime_control_exposes_safe_commands():
    status = build_runtime_control_status()

    commands = status["safe_commands"]
    assert isinstance(commands, list)
    assert len(commands) >= 3
