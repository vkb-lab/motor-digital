from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase68c_mission_runner_files_exist():
    assert (ROOT / "scripts" / "run_kos_autonomy_mission.ps1").exists()
    assert (ROOT / "config" / "kos_autonomy_mission_runner_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMY_MISSION_RUNNER_V068C.md").exists()

def test_phase68c_mission_runner_is_safe_only():
    text = (ROOT / "scripts" / "run_kos_autonomy_mission.ps1").read_text(encoding="utf-8")
    assert "submit_kos_operator_command_batch.ps1" in text
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in text
    assert "instagram_publish_executed = $false" in text
    assert "browser_logged_account_automation_used = $false" in text
    assert "write_json_report" in (ROOT / "config" / "kos_autonomy_mission_runner_policy.json").read_text(encoding="utf-8")
