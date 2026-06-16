from k_atlas.kaizen.local_autonomy_loop import run_local_autonomy_cycle

def test_local_autonomy_loop_is_safe():
    result = run_local_autonomy_cycle(command_limit=1)

    assert result["status"] == "KOS_LOCAL_AUTONOMY_LOOP_CYCLE_COMPLETED"
    assert result["gates"]["execute_generated_commands"] is False
    assert result["gates"]["repo_write_allowed"] is False
    assert result["gates"]["patch_apply_allowed"] is False
    assert result["gates"]["arbitrary_shell_allowed"] is False
    assert result["gates"]["commit_allowed"] is False
    assert result["gates"]["push_allowed"] is False
    assert result["gates"]["deploy_allowed"] is False
    assert result["gates"]["paid_ai_allowed"] is False
    assert result["gates"]["instagram_publish_allowed"] is False
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False

def test_local_autonomy_loop_has_pipeline_keys():
    result = run_local_autonomy_cycle(command_limit=1)

    assert "coworker" in result["pipeline"]
    assert "patch_workspace" in result["pipeline"]
    assert "command_composer" in result["pipeline"]