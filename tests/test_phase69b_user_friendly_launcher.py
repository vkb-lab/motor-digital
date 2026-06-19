from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase69b_launcher_files_exist():
    assert (ROOT / "scripts" / "start_kos_user_launcher.ps1").exists()
    assert (ROOT / "KOS_User_Launcher.cmd").exists()
    assert (ROOT / "pages" / "KOS_User_Launcher.py").exists()
    assert (ROOT / "config" / "kos_user_friendly_launcher_policy.json").exists()
    assert (ROOT / "docs" / "KOS_USER_FRIENDLY_LOCAL_LAUNCHER_V069B.md").exists()

def test_phase69b_launcher_safe_only():
    launcher = (ROOT / "scripts" / "start_kos_user_launcher.ps1").read_text(encoding="utf-8")
    page = (ROOT / "pages" / "KOS_User_Launcher.py").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_user_friendly_launcher_policy.json").read_text(encoding="utf-8")

    assert "submit_kos_operator_command.ps1" in launcher
    assert "run_kos_autonomy_mission.ps1" in launcher
    assert "kos_autonomy_kill_switch.ps1" in page
    assert "browser_logged_account_automation_blocked" in policy
    assert "instagram_publish_blocked" in policy
    assert "paid_ai_locked" in policy
