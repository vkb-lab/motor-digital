$ErrorActionPreference = "Stop"
python scripts/healthcheck.py
python scripts/validate_phase3_client_meta_ops.py
python scripts/run_phase3_client_meta_demo.py
python scripts/run_media_demo.py
python scripts/run_landing_qr_demo.py
python -m pytest tests/test_kos_core.py tests/test_operational_agents.py tests/test_phase2_orchestrator.py tests/test_phase3_client_registry.py tests/test_phase3_agent_delegation.py tests/test_phase3_meta_integrations.py tests/test_phase3_google_business.py tests/test_phase3_media_tools.py tests/test_phase3_attendants.py tests/test_phase3_campaign_studio.py tests/test_phase3_landing_qr.py -q
