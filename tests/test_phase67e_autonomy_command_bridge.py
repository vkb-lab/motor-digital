from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase67e_command_bridge_files_exist():
    assert (ROOT / "scripts" / "create_kos_autonomy_command.ps1").exists()
    assert (ROOT / "config" / "kos_autonomy_command_bridge_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMY_COMMAND_BRIDGE_V067E.md").exists()

def test_phase67e_command_bridge_is_safe_only():
    text = (ROOT / "scripts" / "create_kos_autonomy_command.ps1").read_text(encoding="utf-8")
    assert 'routed_action = "write_json_report"' in text
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in text
    assert "create_kos_autonomous_job.ps1" in text
    assert "instagram_publish_executed = $false" in text
    assert "browser_logged_account_automation_used = $false" in text
