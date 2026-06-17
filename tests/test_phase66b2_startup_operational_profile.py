from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase66b2_files_exist():
    assert (ROOT / "config" / "kos_startup_operational_profile_policy.json").exists()
    assert (ROOT / "scripts" / "start_kos_startup_operational_profile.ps1").exists()
    assert (ROOT / "scripts" / "install_kos_startup_operational_profile.ps1").exists()
    assert (ROOT / "scripts" / "run_phase66b2_startup_operational_profile_status.py").exists()

def test_phase66b2_policy_blocks_external_actions():
    data = json.loads((ROOT / "config" / "kos_startup_operational_profile_policy.json").read_text(encoding="utf-8"))
    forbidden = set(data["forbidden_actions"])
    assert "instagram_publish" in forbidden
    assert "paid_ai_call" in forbidden
    assert "external_deploy" in forbidden
    assert "browser_logged_account_automation" in forbidden

def test_phase66b2_startup_script_mentions_core_ports():
    text = (ROOT / "scripts" / "start_kos_startup_operational_profile.ps1").read_text(encoding="utf-8")
    for port in ["8501", "8507", "8512", "8514", "8515"]:
        assert port in text
    assert "start_kos_local_autonomy_loop.ps1" in text
    assert "start_kos_engineer_handoff_queue_loop.ps1" in text
