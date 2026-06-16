from k_atlas.kaizen.scheduler_gate import build_scheduler_plan, run_scheduler_tick, summarize_scheduler

def test_scheduler_plan_is_manual_only():
    plan = build_scheduler_plan()

    assert plan["status"] == "SCHEDULER_MANUAL_GATE_READY"
    assert plan["windows_task_registered"] is False
    assert plan["auto_start_enabled"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_scheduler_tick_is_safe():
    result = run_scheduler_tick("test_phase42")

    assert result["status"] == "SCHEDULER_TICK_COMPLETED"
    assert result["windows_task_registered"] is False
    assert result["auto_start_enabled"] is False
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
    assert result["external_side_effects_executed"] is False

def test_scheduler_summary_safe():
    summary = summarize_scheduler()

    assert summary["status"] == "SCHEDULER_SUMMARY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
