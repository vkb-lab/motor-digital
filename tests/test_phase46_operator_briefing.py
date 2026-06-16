from k_atlas.kaizen.operator_briefing import build_operator_briefing, render_markdown

def test_operator_briefing_is_safe():
    briefing = build_operator_briefing(write_log=False)

    assert briefing["status"] == "KOS_OPERATOR_DAILY_BRIEFING_READY"
    assert briefing["real_action_executed"] is False
    assert briefing["paid_ai_call_executed"] is False
    assert briefing["instagram_publish_executed"] is False
    assert briefing["external_side_effects_executed"] is False

def test_operator_briefing_has_priorities_and_commands():
    briefing = build_operator_briefing(write_log=False)

    assert isinstance(briefing["priorities"], list)
    assert len(briefing["priorities"]) >= 1
    assert isinstance(briefing["safe_next_commands"], list)
    assert len(briefing["safe_next_commands"]) >= 1

def test_operator_briefing_markdown_renders():
    briefing = build_operator_briefing(write_log=False)
    md = render_markdown(briefing)

    assert "# K-OS Operator Daily Briefing" in md
    assert "Nenhuma publicacao Instagram executada" in md
