from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase70c_files_exist():
    assert (ROOT / "scripts" / "run_kos_chatgpt_conversation_bridge.ps1").exists()
    assert (ROOT / "KOS_ChatGPT_Conversation_Bridge.cmd").exists()
    assert (ROOT / "config" / "kos_chatgpt_conversation_bridge_policy.json").exists()
    assert (ROOT / "docs" / "KOS_CHATGPT_CONVERSATION_BRIDGE_V070C.md").exists()

def test_phase70c_policy_blocks_browser_automation():
    policy = json.loads((ROOT / "config" / "kos_chatgpt_conversation_bridge_policy.json").read_text(encoding="utf-8"))
    assert policy["opens_browser"] is True
    assert policy["browser_logged_account_automation_used"] is False
    assert policy["browser_scraping_enabled"] is False
    assert policy["browser_click_automation_enabled"] is False
    assert policy["reads_chatgpt_ui_automatically"] is False
    assert policy["auto_execution_enabled"] is False
    assert policy["operator_review_required"] is True

def test_phase70c_script_uses_existing_safe_pipeline():
    script = (ROOT / "scripts" / "run_kos_chatgpt_conversation_bridge.ps1").read_text(encoding="utf-8")
    assert "run_kos_engineer_packet_oneclick.ps1" in script
    assert "run_phase69l_engineer_packet_review_console.py" in script
    assert "-ProcessLatest" in script
