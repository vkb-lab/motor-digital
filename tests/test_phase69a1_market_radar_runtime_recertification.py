from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase69a1_recertification_files_exist():
    assert (ROOT / "reports" / "KOS_PHASE69A1_AGENT_OS_MARKET_RADAR_RUNTIME_RECERTIFICATION.json").exists()
    assert (ROOT / "docs" / "KOS_AGENT_OS_MARKET_RADAR_RUNTIME_RECERTIFICATION_V069A1.md").exists()

def test_phase69a1_recertification_safe_flags():
    report = json.loads((ROOT / "reports" / "KOS_PHASE69A1_AGENT_OS_MARKET_RADAR_RUNTIME_RECERTIFICATION.json").read_text(encoding="utf-8"))
    assert report["paid_ai_call_executed"] is False
    assert report["instagram_publish_executed"] is False
    assert report["browser_logged_account_automation_used"] is False
    assert report["production_publish_locked"] is True
    assert report["paid_ai_locked"] is True
