from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase69e2_files_exist():
    assert (ROOT / "pages" / "KOS_Publish_Audit_Panel.py").exists()
    assert (ROOT / "scripts" / "open_kos_publish_audit_panel.ps1").exists()
    assert (ROOT / "KOS_Publish_Audit_Panel.cmd").exists()
    assert (ROOT / "config" / "kos_publish_audit_visual_panel_policy.json").exists()
    assert (ROOT / "docs" / "KOS_PUBLISH_AUDIT_VISUAL_PANEL_V069E2.md").exists()

def test_phase69e2_panel_is_visual_only():
    page = (ROOT / "pages" / "KOS_Publish_Audit_Panel.py").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_publish_audit_visual_panel_policy.json").read_text(encoding="utf-8")

    assert "Publish Audit Panel" in page
    assert "run_phase69e_publish_audit_gate.py" in page
    assert "run_phase69f_human_confirmed_publish_dry_run_gate.py" in page
    assert "run_phase69g_real_publish_approval_ledger.py" in page
    assert "visual_only" in policy
    assert "real_publish_enabled" in policy
    assert "publish_endpoint_called" in policy
    assert "http_post_used" in policy
    assert "parada_atlantida_locked" in policy

def test_phase69e2_user_launcher_patched():
    launcher = ROOT / "pages" / "KOS_User_Launcher.py"
    assert launcher.exists()
    text = launcher.read_text(encoding="utf-8")
    assert "KOS_PHASE69E2_PUBLISH_AUDIT_PANEL_START" in text
