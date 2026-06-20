from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase71b_social_strategy_generator.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase71b", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase71b_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_social_strategy_generator_policy.json").exists()
    assert (ROOT / "docs" / "KOS_SOCIAL_STRATEGY_GENERATOR_V071B.md").exists()


def test_phase71b_generates_hupmix_strategy():
    mod = load_module()
    result = mod.build_strategy(
        target="hupmix",
        objective="validar estrategia segura",
        tone="direto",
        campaign="test",
        strategy_id="test-71b-hupmix",
    )
    assert result["status"] == "KOS_SOCIAL_STRATEGY_READY"
    assert result["target"] == "hupmix"
    assert result["requires_human_approval"] is True
    assert result["audit"]["auto_publish_enabled"] is False
    assert result["audit"]["instagram_publish_executed"] is False
    assert len(result["post_plan"]) >= 3


def test_phase71b_blocks_parada():
    mod = load_module()
    result = mod.build_strategy(
        target="paradaatlantida",
        objective="nao deve passar",
        tone="direto",
        campaign="blocked",
        strategy_id="test-71b-blocked",
    )
    assert result["status"] == "KOS_SOCIAL_STRATEGY_BLOCKED"
    assert result["auto_publish_enabled"] is False
    assert result["instagram_publish_executed"] is False


def test_phase71b_policy_does_not_create_dashboard():
    policy = json.loads((ROOT / "config" / "kos_social_strategy_generator_policy.json").read_text(encoding="utf-8-sig"))
    assert policy["creates_new_dashboard"] is False
    assert policy["dashboard_reuse"]
    assert policy["auto_publish_enabled"] is False
    assert policy["operator_review_required"] is True
