from pathlib import Path

from k_atlas.product_factory.product_local_runner_gate import (
    evaluate_product_local_runner_gate,
    build_product_local_runner_gate_report,
)

def _product(path: str, safe: bool = True):
    return {
        "product_id": "KOS-PRODUCT-TEST",
        "slug": "demo-product",
        "title": "Demo Product",
        "product_type": "saas",
        "path": path,
        "safe": safe,
    }

def test_runner_gate_detects_app_and_tests(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    tests_dir = product_dir / "tests"
    tests_dir.mkdir(parents=True)
    (product_dir / "app.py").write_text("print('ok')", encoding="utf-8")
    (tests_dir / "test_ok.py").write_text("def test_ok(): assert True", encoding="utf-8")

    result = evaluate_product_local_runner_gate(_product(str(product_dir)))

    assert result["status"] == "PRODUCT_LOCAL_RUNNER_GATE_READY"
    assert result["has_app_py"] is True
    assert result["has_tests_dir"] is True
    assert result["gates"]["product_execution_allowed"] is False
    assert result["gates"]["shell_execution_allowed"] is False
    assert result["gates"]["deploy_allowed"] is False
    assert result["gates"]["paid_ai_allowed"] is False
    assert result["gates"]["instagram_publish_allowed"] is False
    assert result["real_action_executed"] is False
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False
    assert all(command["execution_allowed_now"] is False for command in result["manual_commands"])

def test_runner_gate_attention_when_no_app_or_tests(tmp_path):
    product_dir = tmp_path / "products" / "empty-product"
    product_dir.mkdir(parents=True)

    result = evaluate_product_local_runner_gate(_product(str(product_dir)))

    assert result["status"] == "PRODUCT_LOCAL_RUNNER_GATE_ATTENTION_REQUIRED"
    assert "app_py_not_found" in result["attention"]
    assert "tests_folder_not_found" in result["attention"]
    assert result["gates"]["human_review_required"] is True

def test_runner_gate_blocks_unsafe_product(tmp_path):
    product_dir = tmp_path / "products" / "unsafe-product"
    product_dir.mkdir(parents=True)
    (product_dir / "app.py").write_text("print('ok')", encoding="utf-8")

    result = evaluate_product_local_runner_gate(_product(str(product_dir), safe=False))

    assert result["status"] == "PRODUCT_LOCAL_RUNNER_GATE_ATTENTION_REQUIRED"
    assert "product_registry_marked_not_safe" in result["attention"]
    assert result["gates"]["product_execution_allowed"] is False

def test_runner_gate_report_is_read_only(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)
    (product_dir / "app.py").write_text("print('ok')", encoding="utf-8")

    registry = {
        "snapshot": {
            "products": [
                _product(str(product_dir))
            ]
        }
    }

    report = build_product_local_runner_gate_report(registry)

    assert report["status"] == "PRODUCT_LOCAL_RUNNER_GATE_REPORT_READY"
    assert report["products_count"] == 1
    assert report["gates"]["read_only"] is True
    assert report["gates"]["product_execution_allowed"] is False
    assert report["gates"]["shell_execution_allowed"] is False
    assert report["gates"]["deploy_allowed"] is False
    assert report["gates"]["paid_ai_allowed"] is False
    assert report["gates"]["instagram_publish_allowed"] is False
    assert report["real_action_executed"] is False