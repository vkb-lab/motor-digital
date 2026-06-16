from k_atlas.kaizen.local_review_inbox import summarize_review_items, build_review_bundle

def test_review_summary_counts_items():
    commands = [{"title": "cmd"}]
    tasks = [{"title": "task"}]
    orders = [{"title": "order"}]
    drafts = [{"title": "draft"}]

    summary = summarize_review_items(commands, tasks, orders, drafts)

    assert summary["commands_count"] == 1
    assert summary["tasks_count"] == 1
    assert summary["work_orders_count"] == 1
    assert summary["command_drafts_count"] == 1
    assert summary["has_pending_review"] is True

def test_review_bundle_is_safe():
    draft = {
        "draft_id": "DRAFT",
        "title": "Draft",
        "powershell_command": "git --no-pager status --short",
    }

    bundle = build_review_bundle(
        commands=[{"command_id": "CMD", "title": "Command"}],
        tasks=[{"task_id": "TASK", "title": "Task"}],
        work_orders=[{"work_order_id": "WO", "title": "Order"}],
        drafts=[draft],
        loop_status={"status": "OK"},
    )

    assert bundle["status"] == "KOS_LOCAL_REVIEW_BUNDLE_READY"
    assert "git --no-pager status --short" in bundle["bundle_text"]
    assert bundle["gates"]["read_only"] is True
    assert bundle["gates"]["execute_allowed_now"] is False
    assert bundle["gates"]["repo_write_allowed_now"] is False
    assert bundle["gates"]["commit_allowed"] is False
    assert bundle["gates"]["push_allowed"] is False
    assert bundle["gates"]["deploy_allowed"] is False
    assert bundle["gates"]["paid_ai_allowed"] is False
    assert bundle["gates"]["instagram_publish_allowed"] is False
    assert bundle["real_action_executed"] is False

def test_empty_review_bundle_is_safe():
    bundle = build_review_bundle([], [], [], [], {})

    assert bundle["status"] == "KOS_LOCAL_REVIEW_BUNDLE_READY"
    assert "Nenhum command draft disponivel ainda" in bundle["bundle_text"]
    assert bundle["gates"]["human_review_required"] is True