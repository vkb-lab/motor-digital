from k_atlas.kaizen.local_command_composer import build_command_draft_from_work_order

def _work_order():
    return {
        "work_order_id": "KOS-WO-TEST",
        "source_task_id": "KOS-COWORKER-TEST",
        "source_command_id": "KOS-CMD-TEST",
        "title": "Teste command composer",
        "risk": "low",
        "task_type": "local_autonomy_operation",
        "proposed_repo_files": [
            {"path": "config/test_policy.json", "purpose": "Teste"},
            {"path": "tests/test_example.py", "purpose": "Teste"},
        ],
    }

def test_command_draft_is_safe_by_default():
    draft = build_command_draft_from_work_order(_work_order())

    assert draft["status"] == "KOS_LOCAL_COMMAND_DRAFT_READY"
    assert draft["source_work_order_id"] == "KOS-WO-TEST"
    assert draft["gates"]["execute_allowed_now"] is False
    assert draft["gates"]["repo_write_allowed_now"] is False
    assert draft["gates"]["patch_apply_allowed_now"] is False
    assert draft["gates"]["commit_allowed"] is False
    assert draft["gates"]["push_allowed"] is False
    assert draft["gates"]["deploy_allowed"] is False
    assert draft["gates"]["paid_ai_allowed"] is False
    assert draft["gates"]["instagram_publish_allowed"] is False
    assert draft["real_action_executed"] is False
    assert draft["paid_ai_call_executed"] is False
    assert draft["instagram_publish_executed"] is False

def test_command_draft_contains_diagnostics_only():
    draft = build_command_draft_from_work_order(_work_order())
    command = draft["powershell_command"].lower()

    assert "git --no-pager status --short" in command
    assert "kos_runtime_control.ps1" in command
    assert "git commit" not in command
    assert "git push" not in command
    assert "remove-item" not in command
    assert "del " not in command
    assert "invoke-webrequest" not in command

def test_command_draft_lists_files():
    draft = build_command_draft_from_work_order(_work_order())
    command = draft["powershell_command"]

    assert "config/test_policy.json" in command
    assert "tests/test_example.py" in command