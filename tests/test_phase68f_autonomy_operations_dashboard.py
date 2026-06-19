from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase68f_operations_dashboard_files_exist():
    assert (ROOT / "scripts" / "run_phase68f_autonomy_operations_snapshot.py").exists()
    assert (ROOT / "pages" / "KOS_Autonomy_Operations_Dashboard.py").exists()
    assert (ROOT / "config" / "kos_autonomy_operations_dashboard_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMY_OPERATIONS_DASHBOARD_V068F.md").exists()

def test_phase68f_operations_dashboard_is_safe_only():
    script = (ROOT / "scripts" / "run_phase68f_autonomy_operations_snapshot.py").read_text(encoding="utf-8")
    page = (ROOT / "pages" / "KOS_Autonomy_Operations_Dashboard.py").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_autonomy_operations_dashboard_policy.json").read_text(encoding="utf-8")
    assert "instagram_publish_executed" in script
    assert "browser_logged_account_automation_used" in script
    assert "paid_ai_call_executed" in script
    assert "kill_switch_engage_command" in script
    assert "paid_ai_locked" in page
    assert "browser_logged_account_automation_blocked" in policy
