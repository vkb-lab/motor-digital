from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def test_phase70e_files():
    assert (ROOT/"scripts/kos_chatgpt_bridge_runtime_control.ps1").exists()
    assert (ROOT/"config/kos_chatgpt_bridge_runtime_controller_policy.json").exists()
    assert (ROOT/"docs/KOS_CHATGPT_BRIDGE_RUNTIME_CONTROLLER_V070E.md").exists()

def test_phase70e_safe_policy():
    p=json.loads((ROOT/"config/kos_chatgpt_bridge_runtime_controller_policy.json").read_text(encoding="utf-8-sig"))
    assert p["anti_duplicate_guard"] is True
    assert p["auto_execution_enabled"] is False
    assert p["operator_review_required"] is True
    assert p["browser_scraping_enabled"] is False
    assert p["reads_chatgpt_ui_automatically"] is False

def test_phase70e_script_actions():
    s=(ROOT/"scripts/kos_chatgpt_bridge_runtime_control.ps1").read_text(encoding="utf-8-sig")
    assert 'ValidateSet("start","stop","status","restart","logs")' in s
    assert "run_phase70d_chatgpt_bridge_drop_watcher.py" in s
    assert "FindWatcher" in s
