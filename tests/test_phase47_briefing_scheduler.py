from k_atlas.kaizen.briefing_scheduler import run_briefing_scheduler_tick, summarize_briefing_scheduler

def test_briefing_scheduler_tick_is_safe():
    result = run_briefing_scheduler_tick("test_phase47")

    assert result["status"] == "BRIEFING_SCHEDULER_TICK_COMPLETED"
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
    assert result["external_side_effects_executed"] is False

def test_briefing_scheduler_summary_is_safe():
    summary = summarize_briefing_scheduler()

    assert summary["status"] == "BRIEFING_SCHEDULER_SUMMARY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
