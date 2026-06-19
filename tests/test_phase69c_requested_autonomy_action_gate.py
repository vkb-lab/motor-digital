from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69c_requested_autonomy_action_gate.py"

def load_module():
    spec = importlib.util.spec_from_file_location("phase69c_gate", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def test_phase69c_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_requested_autonomy_action_gate_policy.json").exists()
    assert (ROOT / "docs" / "KOS_REQUESTED_AUTONOMY_ACTION_GATE_V069C.md").exists()

def test_phase69c_allows_requested_campaign_continuation():
    mod = load_module()
    result = mod.validate_request("campaign_continue", "prepare_only", False)
    assert result["status"] == "KOS_REQUESTED_AUTONOMY_ACTION_ALLOWED"
    assert result["allowed"] is True

def test_phase69c_blocks_external_publish_without_human_confirmation():
    mod = load_module()
    result = mod.validate_request("instagram_publish", "human_confirmed_only", False)
    assert result["status"] == "KOS_REQUESTED_AUTONOMY_ACTION_BLOCKED"
    assert result["allowed"] is False

def test_phase69c_allows_external_publish_with_human_confirmation_gate_only():
    mod = load_module()
    result = mod.validate_request("instagram_publish", "human_confirmed_only", True)
    assert result["status"] == "KOS_REQUESTED_AUTONOMY_ACTION_ALLOWED"
    assert result["allowed"] is True
    assert result["instagram_publish_executed"] is False
    assert result["browser_logged_account_automation_used"] is False
