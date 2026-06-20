from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase70b_files_exist():
    assert (ROOT / "pages" / "KOS_Safe_Patch_Review_Panel.py").exists()
    assert (ROOT / "scripts" / "open_kos_safe_patch_review_panel.ps1").exists()
    assert (ROOT / "KOS_Safe_Patch_Review_Panel.cmd").exists()
    assert (ROOT / "config" / "kos_safe_patch_review_panel_policy.json").exists()
    assert (ROOT / "docs" / "KOS_SAFE_PATCH_REVIEW_PANEL_V070B.md").exists()

def test_phase70b_panel_is_review_only():
    page = (ROOT / "pages" / "KOS_Safe_Patch_Review_Panel.py").read_text(encoding="utf-8")
    policy = (ROOT / "config" / "kos_safe_patch_review_panel_policy.json").read_text(encoding="utf-8")

    assert "Não aplica patch" in page or "Nao aplica patch" in page
    assert "patch_application_enabled" in page
    assert "operator_review_required" in page
    assert "apply_requires_future_gate" in page
    assert "review_only" in policy
    assert "patch_application_enabled" in policy

def test_phase70b_launcher_patched():
    launcher = ROOT / "pages" / "KOS_User_Launcher.py"
    assert launcher.exists()
    text = launcher.read_text(encoding="utf-8")
    assert "KOS_PHASE70B_SAFE_PATCH_REVIEW_PANEL_START" in text
