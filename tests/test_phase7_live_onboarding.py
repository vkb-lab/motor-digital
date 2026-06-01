from k_atlas.live_onboarding import generate_client_onboarding

def test_client_onboarding_safe():
    result = generate_client_onboarding("parada_atlantida")
    assert result["status"] == "PENDING_APPROVAL"
    assert result["values_saved"] is False
    assert result["real_actions_enabled"] is False
