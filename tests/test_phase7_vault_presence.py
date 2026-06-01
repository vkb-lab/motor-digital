from k_atlas.vault_presence.env_presence_checker import check_env_presence

def test_env_presence_safe():
    result = check_env_presence("instagram")
    assert result["values_exposed"] is False
    assert result["values_saved"] is False
