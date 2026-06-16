from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission, save_blueprint, summarize_blueprints

def test_build_blueprint_is_safe():
    mission = build_product_mission(
        idea="SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )

    blueprint = build_blueprint_from_mission(mission)

    assert blueprint["status"] == "PRODUCT_BLUEPRINT_READY"
    assert blueprint["gates"]["execution_allowed"] is False
    assert blueprint["gates"]["build_allowed"] is False
    assert blueprint["gates"]["deploy_allowed"] is False
    assert blueprint["gates"]["paid_ai_allowed"] is False
    assert blueprint["gates"]["instagram_publish_allowed"] is False
    assert blueprint["real_action_executed"] is False
    assert blueprint["paid_ai_call_executed"] is False
    assert blueprint["instagram_publish_executed"] is False
    assert blueprint["external_side_effects_executed"] is False

def test_blueprint_contains_required_sections():
    mission = build_product_mission(
        idea="Landing page teste",
        product_type="landing_page",
        target_user="lead",
        market="marketing"
    )

    blueprint = build_blueprint_from_mission(mission)

    assert "product_brief" in blueprint
    assert "mvp_scope" in blueprint
    assert "architecture" in blueprint
    assert "automation_plan" in blueprint
    assert "launch_plan" in blueprint
    assert "risk_register" in blueprint
    assert "acceptance_criteria" in blueprint

def test_save_blueprint_and_summary_are_safe():
    mission = build_product_mission(
        idea="Dashboard teste",
        product_type="dashboard",
        target_user="operador",
        market="dados"
    )

    blueprint = build_blueprint_from_mission(mission)
    saved = save_blueprint(blueprint)
    summary = summarize_blueprints(limit=5)

    assert saved["status"] == "PRODUCT_BLUEPRINT_SAVED"
    assert summary["status"] == "PRODUCT_BLUEPRINT_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
