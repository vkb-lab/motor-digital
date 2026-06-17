from k_atlas.kaizen.work_order_route_registry import (
    load_work_order_route_registry,
    proposed_files_for_task,
    route_work_order_task,
    get_work_order_route_registry_status,
)

def _task(title: str, body: str, task_type: str = "general_operation"):
    return {
        "title": title,
        "body": body,
        "classification": {
            "task_type": task_type,
            "risk": "high",
            "ask_k_atlas_engineer": True,
        },
    }

def test_route_registry_loads_routes():
    registry = load_work_order_route_registry()

    assert registry["status"] == "ACTIVE"
    assert len(registry["routes"]) >= 5

def test_phase64_route_wins_over_phase63_mentions():
    task = _task(
        "Fase 64 - Product Export ZIP Writer Gate",
        "Usar Product Export Packager da Fase 63 e exigir YES_CREATE_PRODUCT_EXPORT_ZIP_LOCAL_ONLY.",
    )

    route = route_work_order_task(task)
    paths = [item["path"] for item in route["proposed_files"]]

    assert route["route_id"] == "phase64_product_export_zip_writer_gate"
    assert "k_atlas/product_factory/product_export_zip_writer_gate.py" in paths
    assert "k_atlas/product_factory/product_export_packager.py" not in paths

def test_phase63_route_wins_over_runner_gate_mentions():
    task = _task(
        "Fase 63 - Product Export Packager",
        "Ler Product Registry, QA Gate e Product Local Runner Gate sem criar zip.",
    )

    route = route_work_order_task(task)
    paths = [item["path"] for item in route["proposed_files"]]

    assert route["route_id"] == "phase63_product_export_packager"
    assert "k_atlas/product_factory/product_export_packager.py" in paths
    assert "k_atlas/product_factory/product_local_runner_gate.py" not in paths

def test_phase62_runner_gate_route():
    task = _task(
        "Fase 62 - Product Local Runner Gate",
        "Preparar runner gate local read-only.",
    )

    files = proposed_files_for_task(task)
    paths = [item["path"] for item in files]

    assert "k_atlas/product_factory/product_local_runner_gate.py" in paths

def test_unknown_route_requires_review():
    task = _task(
        "Comando solto sem escopo",
        "fazer alguma coisa depois",
    )

    route = route_work_order_task(task)

    assert route["status"] == "WORK_ORDER_ROUTE_REVIEW_REQUIRED"
    assert route["route_id"] == "unknown_review_required"
    assert route["proposed_files"][0]["path"] == "reports/KOS_LOCAL_WORK_ORDER_REVIEW_REQUIRED.json"

def test_registry_status_is_safe():
    status = get_work_order_route_registry_status()

    assert status["status"] == "WORK_ORDER_ROUTE_REGISTRY_READY"
    assert status["routes_count"] >= 5
    assert status["unknown_route_requires_review"] is True
    assert status["no_command_execution"] is True
    assert status["no_paid_ai"] is True
    assert status["no_instagram"] is True
    assert status["no_deploy"] is True
