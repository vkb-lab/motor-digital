from k_atlas.action_channel_router import route_action_channel

def test_api_first_for_instagram():
    result = route_action_channel("instagram_post")
    assert result["channel"] == "API_DRY_RUN"
    assert result["external_call_executed"] is False

def test_browser_fallback_for_unknown():
    result = route_action_channel("unknown_visual_task")
    assert result["status"] == "BROWSER_MANUAL_BRIDGE_READY"
    assert result["real_browser_action_allowed"] is False
