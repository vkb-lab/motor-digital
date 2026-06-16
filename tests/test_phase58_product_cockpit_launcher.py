from k_atlas.product_factory.product_cockpit_launcher import build_launch_instructions, build_launcher_snapshot

def test_launch_instructions_are_read_only():
    record = {
        "product_id": "KOS-PRODUCT-TEST",
        "slug": "demo-product",
        "title": "Demo Product",
        "product_type": "saas",
        "path": "products/demo-product",
        "safe": True,
        "has_tests": True
    }

    instructions = build_launch_instructions(record)

    assert instructions["status"] == "PRODUCT_LAUNCH_INSTRUCTIONS_READY"
    assert instructions["gates"]["shell_execution_allowed"] is False
    assert instructions["gates"]["product_execution_allowed"] is False
    assert instructions["gates"]["deploy_allowed"] is False
    assert instructions["gates"]["paid_ai_allowed"] is False
    assert instructions["real_action_executed"] is False
    assert all(command["execution_allowed_now"] is False for command in instructions["commands"])

def test_launcher_snapshot_counts_products():
    registry = {
        "snapshot": {
            "products": [
                {
                    "product_id": "one",
                    "slug": "one",
                    "title": "One",
                    "product_type": "saas",
                    "path": "products/one",
                    "safe": True,
                    "has_tests": False
                },
                {
                    "product_id": "two",
                    "slug": "two",
                    "title": "Two",
                    "product_type": "api",
                    "path": "products/two",
                    "safe": False,
                    "has_tests": True
                }
            ]
        }
    }

    snapshot = build_launcher_snapshot(registry)

    assert snapshot["status"] == "PRODUCT_COCKPIT_LAUNCHER_READY"
    assert snapshot["products_count"] == 2
    assert snapshot["safe_products_count"] == 1
    assert snapshot["attention_required_count"] == 1
    assert snapshot["gates"]["read_only"] is True
    assert snapshot["gates"]["product_execution_allowed"] is False
    assert snapshot["real_action_executed"] is False
    assert snapshot["paid_ai_call_executed"] is False
    assert snapshot["instagram_publish_executed"] is False

def test_empty_launcher_snapshot_is_safe():
    snapshot = build_launcher_snapshot({"snapshot": {"products": []}})

    assert snapshot["products_count"] == 0
    assert snapshot["launch_items"] == []
    assert snapshot["gates"]["shell_execution_allowed"] is False
    assert snapshot["external_side_effects_executed"] is False