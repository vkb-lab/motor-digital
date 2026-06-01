from k_atlas.live_onboarding.platform_registry import list_platforms

def test_platforms_registered():
    platforms = [p["platform"] for p in list_platforms()]
    assert "instagram" in platforms
    assert "google_business" in platforms
    assert "stripe" in platforms
