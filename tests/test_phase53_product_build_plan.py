from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint, save_build_plan, summarize_build_plans

def test_build_plan_is_safe():
    mission = build_product_mission(
        idea="SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)

    assert plan["status"] == "PRODUCT_BUILD_PLAN_READY"
    assert plan["gates"]["write_product_code_allowed"] is False
    assert plan["gates"]["build_allowed"] is False
    assert plan["gates"]["deploy_allowed"] is False
    assert plan["gates"]["paid_ai_allowed"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False
    assert plan["external_side_effects_executed"] is False

def test_build_plan_has_required_sections():
    mission = build_product_mission(
        idea="API teste",
        product_type="api",
        target_user="dev",
        market="integracoes"
    )
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)

    assert "suggested_files" in plan
    assert "milestones" in plan
    assert "dry_run_commands" in plan
    assert "test_plan" in plan
    assert "acceptance_criteria" in plan
    assert len(plan["suggested_files"]) >= 1

def test_save_build_plan_and_summary_are_safe():
    mission = build_product_mission(
        idea="Dashboard teste",
        product_type="dashboard",
        target_user="operador",
        market="dados"
    )
    blueprint = build_blueprint_from_mission(mission)
    plan = build_plan_from_blueprint(blueprint)
    saved = save_build_plan(plan)
    summary = summarize_build_plans(limit=5)

    assert saved["status"] == "PRODUCT_BUILD_PLAN_SAVED"
    assert summary["status"] == "PRODUCT_BUILD_PLAN_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
