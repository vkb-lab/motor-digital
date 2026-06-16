from pathlib import Path

from k_atlas.product_factory.product_registry import scan_product_directory, scan_products

def test_scan_product_directory_safe(tmp_path):
    product = tmp_path / "products" / "demo-product"
    (product / "config").mkdir(parents=True)
    (product / "tests").mkdir(parents=True)
    (product / "README.md").write_text("# Demo", encoding="utf-8")
    (product / "config" / "product_policy.json").write_text('{"product_type":"saas"}', encoding="utf-8")
    (product / "tests" / "test_product.py").write_text("def test_ok(): assert True", encoding="utf-8")

    record = scan_product_directory(product)

    assert record["status"] == "PRODUCT_RECORD_READY"
    assert record["slug"] == "demo-product"
    assert record["product_type"] == "saas"
    assert record["has_readme"] is True
    assert record["has_tests"] is True
    assert record["has_policy"] is True
    assert record["safe"] is True
    assert record["execution_allowed"] is False
    assert record["deploy_allowed"] is False
    assert record["paid_ai_allowed"] is False

def test_scan_product_directory_detects_suspicious_file(tmp_path):
    product = tmp_path / "products" / "unsafe-product"
    product.mkdir(parents=True)
    (product / ".env").write_text("SECRET=blocked", encoding="utf-8")

    record = scan_product_directory(product)

    assert record["safe"] is False
    assert ".env" in record["suspicious_files"]
    assert record["real_action_executed"] is False

def test_scan_products_read_only(tmp_path):
    base = tmp_path / "products"
    (base / "one").mkdir(parents=True)
    (base / "one" / "README.md").write_text("# One", encoding="utf-8")

    snapshot = scan_products(base)

    assert snapshot["status"] == "PRODUCT_RUNTIME_REGISTRY_READY"
    assert snapshot["products_count"] == 1
    assert snapshot["gates"]["read_only"] is True
    assert snapshot["gates"]["product_execution_allowed"] is False
    assert snapshot["real_action_executed"] is False
    assert snapshot["paid_ai_call_executed"] is False
    assert snapshot["instagram_publish_executed"] is False