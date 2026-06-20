from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def test_phase71a_files_exist():
    assert (ROOT/"pages/KOS_Social_Ops_Control_Center.py").exists()
    assert (ROOT/"scripts/open_kos_social_ops_control_center.ps1").exists()
    assert (ROOT/"config/kos_social_ops_control_center_policy.json").exists()
    assert (ROOT/"docs/KOS_SOCIAL_OPS_CONTROL_CENTER_V071A.md").exists()

def test_phase71a_policy_safe():
    p=json.loads((ROOT/"config/kos_social_ops_control_center_policy.json").read_text(encoding="utf-8-sig"))
    assert p["target_test_account"]=="hupmix"
    assert p["parada_atlantida_locked"] is True
    assert p["auto_publish_enabled"] is False
    assert p["auto_execution_enabled"] is False
    assert p["operator_review_required"] is True
    assert p["browser_scraping_enabled"] is False
    assert p["paid_ai_locked"] is True
    assert p["instagram_publish_executed"] is False

def test_phase71a_dashboard_safety_text():
    s=(ROOT/"pages/KOS_Social_Ops_Control_Center.py").read_text(encoding="utf-8-sig")
    assert "Nenhum botão aqui publica" in s
    assert "Parada Atlântida" in s or "Parada Atlantida" in s
    assert "Hupmix" in s
