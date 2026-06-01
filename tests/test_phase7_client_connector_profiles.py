from pathlib import Path

def test_client_connector_profiles_exist():
    for client_id in ["parada_atlantida","casa_da_limpeza","cliente_03","cliente_04","cliente_05"]:
        base = Path("clients") / client_id / "connectors"
        assert (base/"live_onboarding.json").exists()
        assert (base/"readiness_matrix.json").exists()
        assert (base/"approval_policy.json").exists()
