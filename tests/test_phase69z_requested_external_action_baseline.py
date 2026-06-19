from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_phase69z_baseline_report_exists():
    path = ROOT / "reports" / "KOS_PHASE69Z_REQUESTED_EXTERNAL_ACTION_GOVERNANCE_BASELINE_CERTIFICATION.json"
    assert path.exists()
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["status"] == "KOS_PHASE69Z_REQUESTED_EXTERNAL_ACTION_GOVERNANCE_BASELINE_CERTIFIED"
    assert report["real_publish_executed"] is False
    assert report["publish_endpoint_called"] is False
    assert report["http_post_used"] is False
    assert report["instagram_publish_executed"] is False
    assert report["browser_logged_account_automation_used"] is False
    assert report["parada_atlantida_locked"] is True

def test_phase69z_baseline_doc_exists():
    assert (ROOT / "docs" / "KOS_REQUESTED_EXTERNAL_ACTION_GOVERNANCE_BASELINE_V0690.md").exists()
