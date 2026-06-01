from k_atlas.public_asset_bridge.public_url_runner import build_phase16_public_url_package

def test_phase16_package_without_deploy_is_safe():
    result = build_phase16_public_url_package(attempt_deploy=False)
    assert result["real_action_executed"] is False
    assert result["instagram_publish_executed"] is False
    assert result["status"] in ["READY_FOR_INSTAGRAM_REAL_IMAGE", "WAITING_PUBLIC_IMAGE_URL"]
