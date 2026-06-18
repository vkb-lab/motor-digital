from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase67a_kill_switch_files_exist():
    assert (ROOT / "scripts" / "kos_autonomy_kill_switch.ps1").exists()
    assert (ROOT / "config" / "kos_autonomy_kill_switch_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMY_KILL_SWITCH_V067A.md").exists()

def test_phase67a_startup_guard_installed():
    text = (ROOT / "scripts" / "start_kos_startup_operational_profile.ps1").read_text(encoding="utf-8")
    assert "KOS_PHASE67A_AUTONOMY_KILL_SWITCH_GUARD_START" in text
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in text
