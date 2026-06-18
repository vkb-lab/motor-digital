from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase68e_mission_queue_loop_files_exist():
    assert (ROOT / "scripts" / "start_kos_autonomy_mission_queue_loop.ps1").exists()
    assert (ROOT / "config" / "kos_autonomy_mission_queue_loop_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMY_MISSION_QUEUE_LOOP_V068E.md").exists()

def test_phase68e_mission_queue_loop_is_safe_only():
    loop = (ROOT / "scripts" / "start_kos_autonomy_mission_queue_loop.ps1").read_text(encoding="utf-8")
    startup = (ROOT / "scripts" / "start_kos_startup_operational_profile.ps1").read_text(encoding="utf-8")
    runtime = (ROOT / "scripts" / "run_phase49_runtime_control_status.py").read_text(encoding="utf-8")

    assert "process_kos_autonomy_mission_queue.ps1" in loop
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in loop
    assert "instagram_publish_executed = $false" in loop
    assert "browser_logged_account_automation_used = $false" in loop
    assert "KOS_PHASE68E_MISSION_QUEUE_LOOP_START" in startup
    assert "mission_queue_loop" in runtime
    assert "start_kos_autonomy_mission_queue_loop.ps1" in runtime
