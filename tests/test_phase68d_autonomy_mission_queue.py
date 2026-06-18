from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase68d_mission_queue_files_exist():
    assert (ROOT / "scripts" / "submit_kos_autonomy_mission_queue.ps1").exists()
    assert (ROOT / "scripts" / "process_kos_autonomy_mission_queue.ps1").exists()
    assert (ROOT / "config" / "kos_autonomy_mission_queue_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMY_MISSION_QUEUE_PROCESSOR_V068D.md").exists()

def test_phase68d_mission_queue_is_safe_only():
    submit = (ROOT / "scripts" / "submit_kos_autonomy_mission_queue.ps1").read_text(encoding="utf-8")
    processor = (ROOT / "scripts" / "process_kos_autonomy_mission_queue.ps1").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_autonomy_mission_queue_policy.json").read_text(encoding="utf-8")

    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in submit
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in processor
    assert "run_kos_autonomy_mission.ps1" in processor
    assert "write_json_report" in policy
    assert "instagram_publish_executed = $false" in submit
    assert "browser_logged_account_automation_used = $false" in processor
