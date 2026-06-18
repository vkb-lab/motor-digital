from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase67d_intake_files_exist():
    assert (ROOT / "scripts" / "create_kos_autonomous_job.ps1").exists()
    assert (ROOT / "config" / "kos_autonomous_job_intake_policy.json").exists()
    assert (ROOT / "docs" / "KOS_AUTONOMOUS_JOB_INTAKE_V067D.md").exists()

def test_phase67d_intake_is_safe_only():
    text = (ROOT / "scripts" / "create_kos_autonomous_job.ps1").read_text(encoding="utf-8")
    assert 'action = "write_json_report"' in text
    assert "KOS_AUTONOMY_KILL_SWITCH_ENGAGED" in text
    assert "instagram_publish_executed = $false" in text
    assert "browser_logged_account_automation_used = $false" in text
