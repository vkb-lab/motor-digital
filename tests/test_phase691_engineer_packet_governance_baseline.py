from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase691_baseline_report_exists_and_is_safe():
    path = ROOT / "reports" / "KOS_PHASE691_ENGINEER_PACKET_GOVERNANCE_BASELINE_CERTIFICATION.json"
    assert path.exists()
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["status"] == "KOS_PHASE691_ENGINEER_PACKET_GOVERNANCE_BASELINE_CERTIFIED"
    assert report["real_publish_executed"] is False
    assert report["publish_endpoint_called"] is False
    assert report["http_post_used"] is False
    assert report["auto_execution_enabled"] is False
    assert report["operator_review_required"] is True
    assert report["instagram_publish_executed"] is False
    assert report["browser_logged_account_automation_used"] is False
    assert report["parada_atlantida_locked"] is True

def test_phase691_baseline_doc_exists():
    assert (ROOT / "docs" / "KOS_ENGINEER_PACKET_GOVERNANCE_BASELINE_V0691.md").exists()
