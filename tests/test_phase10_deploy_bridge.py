from pathlib import Path
from k_atlas.deploy_bridge import build_deploy_manifest, export_public_status, inspect_vercel_readiness

def test_deploy_manifest_safe():
    manifest = build_deploy_manifest()
    assert manifest["status"] == "PRODUCTION_BRIDGE_READY"
    assert manifest["real_publish_enabled"] is False
    assert manifest["external_call_executed"] is False

def test_public_export_created():
    result = export_public_status()
    assert result["status"] == "PUBLIC_EXPORT_READY"
    assert Path(result["index_path"]).exists()
    assert Path(result["status_path"]).exists()

def test_vercel_readiness_is_non_destructive():
    result = inspect_vercel_readiness()
    assert "status" in result
    assert result["status"] in ["VERCEL_READY", "VERCEL_LOGIN_REQUIRED", "VERCEL_CLI_MISSING"]
