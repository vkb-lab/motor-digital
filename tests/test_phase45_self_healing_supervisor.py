from k_atlas.kaizen.self_healing_supervisor import build_recovery_plan, run_self_healing_supervisor

def test_recovery_plan_is_diagnose_only_when_healthy():
    health = {
        "warnings": [],
        "startup_folder": {"installed": True},
        "background_processes": {"running": True},
        "scheduler_last_tick": {"exists": True},
        "git": {"status_short": ""},
        "runtime_locks": {
            "production_publish_locked": True,
            "paid_ai_locked": True,
        },
    }

    plan = build_recovery_plan(health)

    assert plan["status"] == "SELF_HEALING_SUPERVISOR_HEALTHY"
    assert plan["auto_repair_executed"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_recovery_plan_suggests_manual_commands():
    health = {
        "warnings": ["Loop em background nao detectado agora."],
        "startup_folder": {"installed": False},
        "background_processes": {"running": False},
        "scheduler_last_tick": {"exists": False},
        "git": {"status_short": " M example.txt"},
        "runtime_locks": {
            "production_publish_locked": True,
            "paid_ai_locked": True,
        },
    }

    plan = build_recovery_plan(health)

    assert plan["status"] == "SELF_HEALING_SUPERVISOR_ATTENTION_REQUIRED"
    assert len(plan["issues"]) >= 1
    assert len(plan["manual_recovery_commands"]) >= 1
    assert all(cmd["auto_executed"] is False for cmd in plan["manual_recovery_commands"])

def test_supervisor_never_executes_repair():
    report = run_self_healing_supervisor(write_log=False)

    assert report["auto_repair_executed"] is False
    assert report["real_action_executed"] is False
    assert report["paid_ai_call_executed"] is False
    assert report["instagram_publish_executed"] is False
    assert report["external_side_effects_executed"] is False
