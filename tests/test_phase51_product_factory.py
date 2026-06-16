from k_atlas.product_factory.mission_layer import (
    build_product_mission,
    create_product_mission,
    summarize_product_missions,
    export_to_kaizen_mission_dry_run,
)

def test_build_product_mission_is_safe():
    mission = build_product_mission(
        idea="Criar SaaS de teste",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste",
        priority="medium",
        source="test"
    )

    assert mission["status"] == "PRODUCT_FACTORY_MISSION_READY"
    assert mission["gates"]["execution_allowed"] is False
    assert mission["gates"]["paid_ai_allowed"] is False
    assert mission["gates"]["instagram_publish_allowed"] is False
    assert mission["real_action_executed"] is False
    assert mission["paid_ai_call_executed"] is False
    assert mission["instagram_publish_executed"] is False
    assert mission["external_side_effects_executed"] is False

def test_invalid_product_type_defaults_to_saas():
    mission = build_product_mission(
        idea="Produto invalido",
        product_type="unknown",
        target_user="teste",
        market="teste"
    )

    assert mission["product_type"] == "saas"

def test_create_and_summarize_product_mission():
    mission = create_product_mission(
        idea="Landing page de teste",
        product_type="landing_page",
        target_user="teste",
        market="teste",
        source="test_phase51"
    )

    summary = summarize_product_missions(limit=5)

    assert mission["mission_id"]
    assert summary["status"] == "PRODUCT_FACTORY_SUMMARY_READY"
    assert summary["real_action_executed"] is False
    assert summary["paid_ai_call_executed"] is False
    assert summary["instagram_publish_executed"] is False

def test_export_to_kaizen_is_dry_run():
    mission = build_product_mission(
        idea="Agente de teste",
        product_type="agent",
        target_user="operador",
        market="IA"
    )

    export = export_to_kaizen_mission_dry_run(mission)

    assert export["status"] == "PRODUCT_MISSION_EXPORT_DRY_RUN_READY"
    assert export["dry_run"] is True
    assert export["execution_allowed"] is False
    assert export["real_action_executed"] is False
