from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def test_phase701_baseline_report_safe():
    path=ROOT/'reports/KOS_PHASE701_CHATGPT_LOCAL_BRIDGE_BASELINE_CERTIFICATION.json'
    assert path.exists()
    r=json.loads(path.read_text(encoding='utf-8-sig'))
    assert r['status']=='KOS_PHASE701_CHATGPT_LOCAL_BRIDGE_BASELINE_CERTIFIED'
    assert r['auto_execution_enabled'] is False
    assert r['operator_review_required'] is True
    assert r['browser_scraping_enabled'] is False
    assert r['browser_logged_account_automation_used'] is False
    assert r['reads_chatgpt_ui_automatically'] is False
    assert r['applies_patch_automatically'] is False
    assert r['instagram_publish_executed'] is False
    assert r['real_action_executed'] is False

def test_phase701_baseline_doc_exists():
    assert (ROOT/'docs/KOS_CHATGPT_LOCAL_BRIDGE_BASELINE_V0701.md').exists()
