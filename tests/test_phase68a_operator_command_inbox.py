from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase68a_operator_command_inbox_files_exist():
    assert (ROOT / "scripts" / "submit_kos_operator_command.ps1").exists()
    assert (ROOT / "config" / "kos_operator_command_inbox_policy.json").exists()
    assert (ROOT / "docs" / "KOS_OPERATOR_COMMAND_INBOX_V068A.md").exists()

def test_phase68a_operator_command_inbox_is_safe_only():
    text = (ROOT / "scripts" / "submit_kos_operator_command.ps1").read_text(encoding="utf-8")
    assert "create_kos_autonomy_command.ps1" in text
    assert "run_phase67b_autonomous_job_runner.py" in text
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in text
    assert "instagram_publish_executed = $false" in text
    assert "browser_logged_account_automation_used = $false" in text
