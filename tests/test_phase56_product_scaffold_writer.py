from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint
from k_atlas.product_factory.scaffold_preview import build_scaffold_preview_from_build_plan
from k_atlas.product_factory.scaffold_writer import (
    build_scaffold_write_plan,
    write_scaffold_from_preview,
    CONFIRMATION_PHRASE,
)

def _preview():
    mission = build_product_mission(
        idea="SaaS teste writer",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    return build_scaffold_preview_from_build_plan(build_plan)

def test_write_plan_is_safe():
    plan = build_scaffold_write_plan(_preview())

    assert plan["status"] == "PRODUCT_SCAFFOLD_WRITE_PLAN_READY"
    assert plan["write_allowed_without_confirmation"] is False
    assert plan["real_action_executed"] is False
    assert plan["paid_ai_call_executed"] is False
    assert plan["instagram_publish_executed"] is False

def test_writer_blocks_without_confirmation():
    result = write_scaffold_from_preview(_preview(), confirmation="WRONG", dry_run=False)

    assert result["status"] == "PRODUCT_SCAFFOLD_WRITE_BLOCKED"
    assert result["confirmation_valid"] is False
    assert result["real_action_executed"] is False
    assert result["created_files"] == []

def test_writer_dry_run_even_with_confirmation():
    result = write_scaffold_from_preview(_preview(), confirmation=CONFIRMATION_PHRASE, dry_run=True)

    assert result["status"] == "PRODUCT_SCAFFOLD_WRITE_DRY_RUN"
    assert result["confirmation_valid"] is True
    assert result["dry_run"] is True
    assert result["real_action_executed"] is False