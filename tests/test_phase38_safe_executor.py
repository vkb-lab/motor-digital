from k_atlas.kaizen.safe_executor import is_allowed_action, run_action, list_safe_actions

def test_allowlist_contains_expected_actions():
    actions = list_safe_actions()
    assert "git_status" in actions
    assert "git_branch" in actions
    assert "pytest_phase37" in actions

def test_unknown_action_is_blocked():
    result = run_action("instagram_publish")
    assert result["ok"] is False
    assert result["status"] == "ACTION_BLOCKED"
    assert result["real_action_executed"] is False

def test_dry_run_does_not_execute():
    result = run_action("git_status", dry_run=True)
    assert result["ok"] is True
    assert result["status"] == "DRY_RUN_ACTION_APPROVED"
    assert result["executed"] is False
    assert result["real_action_executed"] is False
