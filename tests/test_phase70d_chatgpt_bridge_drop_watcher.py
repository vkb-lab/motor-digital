from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase70d_files_exist():
    assert (ROOT / "scripts" / "run_phase70d_chatgpt_bridge_drop_watcher.py").exists()
    assert (ROOT / "scripts" / "start_kos_chatgpt_bridge_drop_watcher.ps1").exists()
    assert (ROOT / "KOS_ChatGPT_Bridge_Drop_Watcher.cmd").exists()
    assert (ROOT / "config" / "kos_chatgpt_bridge_drop_watcher_policy.json").exists()
    assert (ROOT / "docs" / "KOS_CHATGPT_BRIDGE_DROP_WATCHER_V070D.md").exists()

def test_phase70d_policy_is_safe_bridge_only():
    policy = json.loads((ROOT / "config" / "kos_chatgpt_bridge_drop_watcher_policy.json").read_text(encoding="utf-8"))
    assert policy["browser_logged_account_automation_used"] is False
    assert policy["browser_scraping_enabled"] is False
    assert policy["browser_click_automation_enabled"] is False
    assert policy["reads_chatgpt_ui_automatically"] is False
    assert policy["auto_execution_enabled"] is False
    assert policy["operator_review_required"] is True
    assert policy["uses_engineer_packet_oneclick"] is True
    assert policy["uses_engineer_packet_review"] is True

def test_phase70d_script_uses_safe_pipeline():
    script = (ROOT / "scripts" / "run_phase70d_chatgpt_bridge_drop_watcher.py").read_text(encoding="utf-8")
    assert "run_kos_engineer_packet_oneclick.ps1" in script
    assert "run_phase69l_engineer_packet_review_console.py" in script
    assert "browser_scraping_enabled" in script
    assert "auto_execution_enabled" in script

def test_phase70d_launcher_patched():
    launcher = ROOT / "pages" / "KOS_User_Launcher.py"
    assert launcher.exists()
    text = launcher.read_text(encoding="utf-8")
    assert "KOS_PHASE70D_CHATGPT_BRIDGE_DROP_WATCHER_START" in text
