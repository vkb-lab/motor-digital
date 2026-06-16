from k_atlas.kaizen.local_patch_workspace import build_work_order_from_task, proposed_files_for_task

def _task(task_type="local_autonomy_operation", body="Fase 61B Local Patch Workspace"):
    return {
        "task_id": "KOS-COWORKER-TEST",
        "source_command_id": "KOS-CMD-TEST",
        "title": "Teste",
        "area": "runtime",
        "priority": "alta",
        "body": body,
        "classification": {
            "task_type": task_type,
            "risk": "low",
            "risk_reasons": [],
            "ask_k_atlas_engineer": False,
        }
    }

def test_proposed_files_for_local_autonomy():
    files = proposed_files_for_task(_task())

    paths = [item["path"] for item in files]
    assert "k_atlas/kaizen/local_patch_workspace.py" in paths
    assert "tests/test_phase61b_local_patch_workspace.py" in paths

def test_work_order_is_safe_by_default():
    order = build_work_order_from_task(_task())

    assert order["status"] == "KOS_LOCAL_PATCH_WORK_ORDER_READY"
    assert order["source_task_id"] == "KOS-COWORKER-TEST"
    assert order["gates"]["repo_write_allowed_now"] is False
    assert order["gates"]["patch_apply_allowed_now"] is False
    assert order["gates"]["arbitrary_shell_allowed"] is False
    assert order["gates"]["commit_allowed"] is False
    assert order["gates"]["push_allowed"] is False
    assert order["gates"]["deploy_allowed"] is False
    assert order["gates"]["paid_ai_allowed"] is False
    assert order["gates"]["instagram_publish_allowed"] is False
    assert order["real_action_executed"] is False
    assert order["paid_ai_call_executed"] is False
    assert order["instagram_publish_executed"] is False

def test_medium_risk_requires_engineer():
    task = _task(body="precisa tag e push")
    task["classification"]["risk"] = "medium"
    task["classification"]["ask_k_atlas_engineer"] = True

    order = build_work_order_from_task(task)

    assert order["gates"]["ask_k_atlas_engineer"] is True
    assert order["gates"]["human_review_required"] is True

def test_operator_command_preview_is_non_destructive():
    order = build_work_order_from_task(_task())
    command = order["operator_command_preview"].lower()

    assert "git --no-pager status --short" in command
    assert "git commit" not in command
    assert "git push" not in command
    assert "remove-item" not in command
    assert "del " not in command


def test_phase63_export_packager_route_wins_over_runner_gate_mentions():
    task = {
        "task_id": "KOS-COWORKER-PHASE63",
        "source_command_id": "KOS-CMD-PHASE63",
        "title": "Fase 63 - Product Export Packager",
        "area": "product_factory",
        "priority": "alta",
        "body": "Criar Fase 63 Product Export Packager. Ler Product Registry, QA Gate e Product Local Runner Gate. Gerar manifesto exportavel sem zip automatico.",
        "classification": {
            "task_type": "general_operation",
            "risk": "high",
            "risk_reasons": [],
            "ask_k_atlas_engineer": True,
        },
    }

    files = proposed_files_for_task(task)
    paths = [item["path"] for item in files]

    assert "k_atlas/product_factory/product_export_packager.py" in paths
    assert "scripts/run_phase63_product_export_packager.py" in paths
    assert "tests/test_phase63_product_export_packager.py" in paths
    assert "k_atlas/product_factory/product_local_runner_gate.py" not in paths
    assert "scripts/run_phase62_product_local_runner_gate.py" not in paths

