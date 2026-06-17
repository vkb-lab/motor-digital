from k_atlas.product_factory.product_export_packager import (
    scan_product_export_files,
    build_product_export_manifest,
    build_product_export_packager_report,
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

def test_export_scan_allows_safe_files_and_blocks_sensitive_files(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)

    (product_dir / "app.py").write_text("print('ok')", encoding="utf-8")
    (product_dir / "README.md").write_text("# Demo", encoding="utf-8")
    (product_dir / ".env").write_text("TOKEN=secret", encoding="utf-8")
    (product_dir / "credentials.json").write_text("{}", encoding="utf-8")

    scan = scan_product_export_files(_product(str(product_dir)))

    allowed = [item["relative_to_product"] for item in scan["allowed_files"]]
    blocked = [item["relative_to_product"] for item in scan["blocked_files"]]

    assert "app.py" in allowed
    assert "README.md" in allowed
    assert ".env" in blocked
    assert "credentials.json" in blocked

def test_export_manifest_blocks_zip_creation_and_deploy(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)
    (product_dir / "app.py").write_text("print('ok')", encoding="utf-8")

    manifest = build_product_export_manifest(_product(str(product_dir)))

    assert manifest["status"] == "PRODUCT_EXPORT_MANIFEST_READY"
    assert manifest["gates"]["read_only"] is True
    assert manifest["gates"]["package_creation_allowed"] is False
    assert manifest["gates"]["zip_creation_allowed"] is False
    assert manifest["gates"]["copy_files_allowed"] is False
    assert manifest["gates"]["shell_execution_allowed"] is False
    assert manifest["gates"]["deploy_allowed"] is False
    assert manifest["gates"]["paid_ai_allowed"] is False
    assert manifest["gates"]["instagram_publish_allowed"] is False
    assert manifest["future_zip_plan"]["zip_creation_allowed_now"] is False
    assert manifest["real_action_executed"] is False
    assert manifest["paid_ai_call_executed"] is False
    assert manifest["instagram_publish_executed"] is False

def test_export_manifest_attention_when_product_not_safe(tmp_path):
    product_dir = tmp_path / "products" / "unsafe-product"
    product_dir.mkdir(parents=True)
    (product_dir / "app.py").write_text("print('ok')", encoding="utf-8")

    manifest = build_product_export_manifest(_product(str(product_dir), safe=False))

    assert manifest["status"] == "PRODUCT_EXPORT_MANIFEST_ATTENTION_REQUIRED"
    assert "product_registry_marked_not_safe" in manifest["attention"]
    assert manifest["gates"]["human_review_required"] is True

def test_export_packager_report_is_read_only(tmp_path):
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

    report = build_product_export_packager_report(
        registry_payload=registry,
        qa_snapshot={"status": "QA_OK"},
        runner_snapshot={"status": "RUNNER_OK"},
    )

    assert report["status"] == "PRODUCT_EXPORT_PACKAGER_REPORT_READY"
    assert report["products_count"] == 1
    assert report["gates"]["read_only"] is True
    assert report["gates"]["package_creation_allowed"] is False
    assert report["gates"]["zip_creation_allowed"] is False
    assert report["gates"]["deploy_allowed"] is False
    assert report["gates"]["paid_ai_allowed"] is False
    assert report["gates"]["instagram_publish_allowed"] is False
    assert report["real_action_executed"] is False