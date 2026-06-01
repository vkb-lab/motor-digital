import os
from k_atlas.ig_real_gate.readiness import inspect_ig_real_readiness
from k_atlas.ig_real_gate.publisher_gate import build_ig_publish_package, execute_ig_real_publish

def test_ig_readiness_safe_without_env(monkeypatch):
    for key in ["IG_BUSINESS_ACCOUNT_ID", "META_ACCESS_KEY", "KOS_REAL_IG_PUBLISH_ENABLED", "KOS_HUMAN_OK_FOR_IG_REAL"]:
        monkeypatch.delenv(key, raising=False)

    result = inspect_ig_real_readiness()
    assert result["status"] == "IG_REAL_LOCKED"
    assert result["can_run_real"] is False

def test_ig_package_blocks_real_without_final_ok(monkeypatch):
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "demo_ig")
    monkeypatch.setenv("META_ACCESS_KEY", "demo_key")
    monkeypatch.delenv("KOS_REAL_IG_PUBLISH_ENABLED", raising=False)
    monkeypatch.delenv("KOS_HUMAN_OK_FOR_IG_REAL", raising=False)

    package = build_ig_publish_package()
    result = execute_ig_real_publish(package)

    assert package["status"] == "READY_FOR_HUMAN_FINAL_OK"
    assert result["status"] == "BLOCKED_BY_REAL_GATE"
    assert result["real_action_executed"] is False
    assert result["external_call_executed"] is False
