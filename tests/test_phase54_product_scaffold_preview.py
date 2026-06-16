from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint
from k_atlas.product_factory.scaffold_preview import build_scaffold_preview_from_build_plan, save_scaffold_preview, summarize_scaffold_previews

def test_scaffold_preview_is_safe():
    mission = build_product_mission(
        idea="SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    preview = build_scaffold_preview_from_build_plan(build_plan)

    assert preview["status"] == "PRODUCT_SCAFFOLD_PREVIEW_READY"
    assert preview["gates"]["write_product_files_allowed"] is False
    assert preview["gates"]["build_allowed"] is False
    assert preview["gates"]["deploy_allowed"] is False
    assert preview["gates"]["paid_ai_allowed"] is False
    assert preview["real_action_executed"] is False
    assert preview["paid_ai_call_executed"] is False
    assert preview["instagram_publish_executed"] is False
    assert preview["external_side_effects_executed"] is False

def test_scaffold_preview_has_files_and_directories():
    mission = build_product_mission(
        idea="API teste",
        product_type="api",
        target_user="dev",
        market="integracoes"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    preview = build_scaffold_preview_from_build_plan(build_plan)

    assert "directories_preview" in preview
    assert "files_preview" in preview
    assert len(preview["files_preview"]) >= 1
    assert all(item["execution_allowed"] is False for item in preview["files_preview"])

def test_save_scaffold_preview_and_summary_are_safe():
    mission = build_product_mission(
        idea="Dashboard teste",
        product_type="dashboard",
        target_user="operador",
        market="dados"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    preview = build_scaffold_preview_from_build_plan(build_plan)
    saved = save_scaffold_preview(preview)
    summary = summarize_scaffold_previews(limit=5)

    assert saved["status"] == "PRODUCT_SCAFFOLD_PREVIEW_SAVED"
    assert summary["status"] == "PRODUCT_SCAFFOLD_PREVIEW_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False
