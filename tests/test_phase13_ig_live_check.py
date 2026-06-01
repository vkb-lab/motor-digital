from k_atlas.ig_live_check.live_check_runner import build_live_ready_package
from k_atlas.ig_live_check.final_live_check import build_final_live_check
from k_atlas.ig_live_check.env_plan import build_env_plan

def test_env_plan_exists():
    plan = build_env_plan()
    assert plan["status"] == "ENV_PLAN_READY"
    assert "IG_BUSINESS_ACCOUNT_ID" in plan["required_names"]
    assert "META_ACCESS_KEY" in plan["required_names"]

def test_live_check_locked_by_default(monkeypatch):
    for key in [
        "IG_BUSINESS_ACCOUNT_ID",
        "META_ACCESS_KEY",
        "KOS_REAL_IG_PUBLISH_ENABLED",
        "KOS_HUMAN_OK_FOR_IG_REAL",
        "KOS_PHASE12_REAL_RUN",
        "KOS_PHASE13_REAL_RUN",
    ]:
        monkeypatch.delenv(key, raising=False)

    result = build_final_live_check(load_runtime=False)
    assert result["status"] == "LIVE_CHECK_LOCKED"
    assert result["ready_for_real_first_post"] is False
    assert result["real_action_executed"] is False

def test_package_does_not_execute_real():
    package = build_live_ready_package()
    assert package["real_action_executed"] is False
    assert package["external_call_executed"] is False
