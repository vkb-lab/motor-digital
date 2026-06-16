from k_atlas.kaizen.autonomy_dashboard import build_autonomy_snapshot, redact_line

def test_redact_line_hides_sensitive_values():
    assert redact_line("TOKEN=abc123") == "TOKEN=<redacted>"
    assert redact_line("OPENAI_API_KEY=abc123") == "OPENAI_API_KEY=<redacted>"
    assert redact_line("NORMAL=value") == "NORMAL=value"

def test_snapshot_is_read_only_and_safe():
    snapshot = build_autonomy_snapshot(write_log=False)

    assert snapshot["status"] == "KOS_AUTONOMY_DASHBOARD_SNAPSHOT"
    assert snapshot["real_action_executed"] is False
    assert snapshot["paid_ai_call_executed"] is False
    assert snapshot["instagram_publish_executed"] is False
    assert snapshot["external_side_effects_executed"] is False

def test_runtime_locks_have_expected_flags():
    snapshot = build_autonomy_snapshot(write_log=False)
    locks = snapshot["runtime_locks"]

    assert locks["parada_atlantida_locked"] is True
    assert locks["hupmix_test_only"] is True
