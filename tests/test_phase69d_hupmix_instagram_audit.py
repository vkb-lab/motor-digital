from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase69d_hupmix_audit_files_exist():
    assert (ROOT / "scripts" / "run_phase69d_hupmix_instagram_audit.py").exists()
    assert (ROOT / "config" / "kos_hupmix_instagram_audit_policy.json").exists()
    assert (ROOT / "docs" / "KOS_HUPMIX_INSTAGRAM_AUDIT_CONNECTOR_V069D.md").exists()

def test_phase69d_hupmix_audit_safe_only():
    script = (ROOT / "scripts" / "run_phase69d_hupmix_instagram_audit.py").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_hupmix_instagram_audit_policy.json").read_text(encoding="utf-8")

    assert "HUPMIX_IG_ID = \"17841471706662294\"" in script
    assert "EXPECTED_USERNAME = \"hupmix\"" in script
    assert "method=\"GET\"" in script
    assert "instagram_publish_executed" in script
    assert "browser_logged_account_automation_used" in script
    assert "parada_atlantida_locked" in policy
    assert "instagram_publish_blocked" in policy
    assert "token_must_not_be_logged" in policy

def test_phase69d_hupmix_audit_does_not_contain_token_literal():
    script = (ROOT / "scripts" / "run_phase69d_hupmix_instagram_audit.py").read_text(encoding="utf-8")
    assert "access_token=" not in script
