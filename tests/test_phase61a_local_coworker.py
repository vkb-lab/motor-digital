from k_atlas.kaizen.local_coworker import classify_command, build_task_from_command, SAFE_DIAGNOSTIC_COMMANDS

def test_classify_autonomy_command():
    command = {
        "title": "Autonomia local com Ollama",
        "body": "Criar coworker local para trabalhar sem Codex",
        "area": "runtime",
    }

    result = classify_command(command)

    assert result["task_type"] == "local_autonomy_operation"
    assert result["risk"] in {"low", "medium", "high"}

def test_build_task_is_safe_by_default():
    command = {
        "command_id": "KOS-CMD-TEST",
        "title": "Fase 61A",
        "body": "Preparar coworker local",
        "priority": "alta",
        "area": "runtime",
    }

    task = build_task_from_command(
        command,
        ollama_status={"available": False, "status": "OLLAMA_NOT_AVAILABLE", "paid_ai_used": False},
        diagnostics={},
    )

    assert task["status"] == "KOS_LOCAL_COWORKER_TASK_READY"
    assert task["source_command_id"] == "KOS-CMD-TEST"
    assert task["autonomy"]["can_read_command_bridge"] is True
    assert task["autonomy"]["can_create_task_capsule"] is True
    assert task["autonomy"]["can_write_repo_files"] is False
    assert task["autonomy"]["can_execute_arbitrary_shell"] is False
    assert task["autonomy"]["can_commit"] is False
    assert task["autonomy"]["can_push"] is False
    assert task["autonomy"]["can_use_paid_ai"] is False
    assert task["gates"]["repo_write_allowed"] is False
    assert task["gates"]["deploy_allowed"] is False
    assert task["real_action_executed"] is False
    assert task["paid_ai_call_executed"] is False
    assert task["instagram_publish_executed"] is False

def test_safe_diagnostic_commands_are_allowlisted():
    assert "git_status" in SAFE_DIAGNOSTIC_COMMANDS
    assert "git_log" in SAFE_DIAGNOSTIC_COMMANDS
    assert "runtime_status" in SAFE_DIAGNOSTIC_COMMANDS
    assert all("rm " not in command.lower() for command in SAFE_DIAGNOSTIC_COMMANDS.values())
    assert all("del " not in command.lower() for command in SAFE_DIAGNOSTIC_COMMANDS.values())