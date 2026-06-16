from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint
from k_atlas.product_factory.scaffold_preview import build_scaffold_preview_from_build_plan
from k_atlas.product_factory.scaffold_writer_gate import (
    build_scaffold_writer_gate,
    evaluate_confirmation,
    CONFIRMATION_PHRASE,
)

def _preview():
    mission = build_product_mission(
        idea="SaaS teste gate",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    return build_scaffold_preview_from_build_plan(build_plan)

def test_writer_gate_is_safe_by_default():
    gate = build_scaffold_writer_gate(_preview())

    assert gate["status"] == "PRODUCT_SCAFFOLD_WRITER_GATE_READY"
    assert gate["gates"]["write_product_files_allowed"] is False
    assert gate["gates"]["create_directories_allowed"] is False
    assert gate["gates"]["build_allowed"] is False
    assert gate["gates"]["deploy_allowed"] is False
    assert gate["gates"]["paid_ai_allowed"] is False
    assert gate["real_action_executed"] is False
    assert gate["paid_ai_call_executed"] is False
    assert gate["instagram_publish_executed"] is False
    assert gate["external_side_effects_executed"] is False

def test_confirmation_valid_but_still_dry_run_only():
    gate = build_scaffold_writer_gate(_preview())
    result = evaluate_confirmation(gate, CONFIRMATION_PHRASE)

    assert result["confirmation_valid"] is True
    assert result["approved_for_future_phase56"] is True
    assert result["write_product_files_allowed_now"] is False
    assert result["phase55_still_dry_run_only"] is True
    assert result["real_action_executed"] is False

def test_confirmation_invalid():
    gate = build_scaffold_writer_gate(_preview())
    result = evaluate_confirmation(gate, "WRONG")

    assert result["confirmation_valid"] is False
    assert result["approved_for_future_phase56"] is False
    assert result["write_product_files_allowed_now"] is False
