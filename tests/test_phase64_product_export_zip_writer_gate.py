import zipfile

from k_atlas.product_factory.product_export_zip_writer_gate import (
    CONFIRMATION_PHRASE,
    validate_manifest_for_zip,
    build_zip_writer_gate_report,
    create_product_export_zip,
)

def _manifest(product_dir, blocked_files=None, status="PRODUCT_EXPORT_MANIFEST_READY"):
    app = product_dir / "app.py"
    readme = product_dir / "README.md"
    app.write_text("print('ok')", encoding="utf-8")
    readme.write_text("# Demo", encoding="utf-8")

    return {
        "status": status,
        "slug": "demo-product",
        "title": "Demo Product",
        "allowed_files": [
            {
                "path": str(app),
                "relative_to_product": "app.py",
                "size_bytes": app.stat().st_size,
            },
            {
                "path": str(readme),
                "relative_to_product": "README.md",
                "size_bytes": readme.stat().st_size,
            },
        ],
        "blocked_files": blocked_files or [],
    }

def test_zip_writer_validation_ready_for_clean_manifest(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)

    validation = validate_manifest_for_zip(_manifest(product_dir), root=tmp_path)

    assert validation["status"] == "PRODUCT_EXPORT_ZIP_VALIDATION_READY"
    assert validation["files_to_zip_count"] == 2
    assert validation["zip_creation_allowed_now"] is False
    assert validation["gates"]["zip_creation_requires_confirmation"] is True
    assert validation["gates"]["deploy_allowed"] is False
    assert validation["gates"]["paid_ai_allowed"] is False
    assert validation["gates"]["instagram_publish_allowed"] is False
    assert validation["real_action_executed"] is False

def test_zip_writer_blocks_manifest_with_blocked_files(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)

    validation = validate_manifest_for_zip(
        _manifest(product_dir, blocked_files=[{"path": str(product_dir / ".env")}]),
        root=tmp_path,
    )

    assert validation["status"] == "PRODUCT_EXPORT_ZIP_VALIDATION_BLOCKED"
    assert "manifest_has_blocked_files" in validation["validation_errors"]

def test_zip_writer_blocks_sensitive_allowed_file_recheck(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)
    env_file = product_dir / ".env"
    env_file.write_text("TOKEN=secret", encoding="utf-8")

    manifest = {
        "status": "PRODUCT_EXPORT_MANIFEST_READY",
        "slug": "demo-product",
        "title": "Demo Product",
        "allowed_files": [
            {
                "path": str(env_file),
                "relative_to_product": ".env",
                "size_bytes": env_file.stat().st_size,
            }
        ],
        "blocked_files": [],
    }

    validation = validate_manifest_for_zip(manifest, root=tmp_path)

    assert validation["status"] == "PRODUCT_EXPORT_ZIP_VALIDATION_BLOCKED"
    assert validation["validation_errors"]

def test_zip_writer_gate_report_is_safe_by_default(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)

    report = build_zip_writer_gate_report(
        export_packager_payload={"report": {"manifests": [_manifest(product_dir)]}},
        root=tmp_path,
    )

    assert report["status"] == "PRODUCT_EXPORT_ZIP_WRITER_GATE_REPORT_READY"
    assert report["ready_for_zip_count"] == 1
    assert report["gates"]["zip_creation_allowed_by_default"] is False
    assert report["gates"]["zip_creation_allowed_only_with_confirmation"] is True
    assert report["gates"]["deploy_allowed"] is False
    assert report["gates"]["paid_ai_allowed"] is False
    assert report["gates"]["instagram_publish_allowed"] is False
    assert report["real_action_executed"] is False

def test_zip_creation_blocked_without_confirmation(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)

    result = create_product_export_zip(
        product_slug="demo-product",
        confirmation="NO",
        export_packager_payload={"report": {"manifests": [_manifest(product_dir)]}},
        root=tmp_path,
        output_dir=tmp_path / "exports",
    )

    assert result["status"] == "PRODUCT_EXPORT_ZIP_CREATION_BLOCKED"
    assert result["zip_created"] is False
    assert result["real_action_executed"] is False

def test_zip_creation_with_confirmation_uses_only_allowed_files(tmp_path):
    product_dir = tmp_path / "products" / "demo-product"
    product_dir.mkdir(parents=True)
    output_dir = tmp_path / "exports"

    result = create_product_export_zip(
        product_slug="demo-product",
        confirmation=CONFIRMATION_PHRASE,
        export_packager_payload={"report": {"manifests": [_manifest(product_dir)]}},
        root=tmp_path,
        output_dir=output_dir,
    )

    assert result["status"] == "PRODUCT_EXPORT_ZIP_CREATED"
    assert result["zip_created"] is True
    assert result["real_action_executed"] is True
    assert result["paid_ai_call_executed"] is False
    assert result["instagram_publish_executed"] is False

    zip_path = tmp_path / result["zip_path"]
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = sorted(zf.namelist())

    assert names == ["README.md", "app.py"]