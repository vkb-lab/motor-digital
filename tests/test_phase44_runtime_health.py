from k_atlas.kaizen.runtime_health import build_runtime_health, check_scheduler_tick, check_background_processes

def test_runtime_health_is_read_only():
    health = build_runtime_health(write_log=False)

    assert health["status"] == "KOS_RUNTIME_HEALTH_CHECK_COMPLETED"
    assert health["real_action_executed"] is False
    assert health["paid_ai_call_executed"] is False
    assert health["instagram_publish_executed"] is False
    assert health["external_side_effects_executed"] is False

def test_scheduler_tick_check_safe_flags():
    tick = check_scheduler_tick()

    assert tick["status"] == "SCHEDULER_LAST_TICK_CHECKED"
    assert tick["real_action_executed"] is False
    assert tick["paid_ai_call_executed"] is False
    assert tick["instagram_publish_executed"] is False

def test_background_process_check_is_read_only():
    result = check_background_processes()

    assert result["status"] == "BACKGROUND_PROCESS_CHECKED"
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
