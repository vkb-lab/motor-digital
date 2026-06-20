from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase71c_social_publish_readiness_auditor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase71c", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase71c_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_social_publish_readiness_auditor_policy.json").exists()
    assert (ROOT / "docs" / "KOS_SOCIAL_PUBLISH_READINESS_AUDITOR_V071C.md").exists()


def test_phase71c_ready_with_https_asset_and_caption():
    mod = load_module()
    result = mod.build_readiness(
        target="hupmix",
        asset_url="https://example.com/hupmix-test.png",
        caption="Legenda final de teste para Hupmix.",
        readiness_id="test-71c-ready",
    )
    assert result["status"] == "KOS_SOCIAL_PUBLISH_READINESS_READY_FOR_HUMAN_REVIEW"
    assert result["creates_new_publish_executor"] is False
    assert result["instagram_publish_executed"] is False
    assert result["publish_endpoint_called"] is False
    assert result["http_post_used"] is False


def test_phase71c_not_ready_without_asset():
    mod = load_module()
    result = mod.build_readiness(
        target="hupmix",
        asset_url="",
        caption="Legenda valida mas sem imagem HTTPS.",
        readiness_id="test-71c-not-ready",
    )
    assert result["status"] == "KOS_SOCIAL_PUBLISH_READINESS_NOT_READY"
    assert result["instagram_publish_executed"] is False


def test_phase71c_parada_not_ready():
    mod = load_module()
    result = mod.build_readiness(
        target="paradaatlantida",
        asset_url="https://example.com/test.png",
        caption="Legenda valida para alvo bloqueado.",
        readiness_id="test-71c-parada",
    )
    assert result["status"] == "KOS_SOCIAL_PUBLISH_READINESS_NOT_READY"
    assert result["parada_atlantida_locked"] is True
    assert result["instagram_publish_executed"] is False


def test_phase71c_policy_reuses_existing_path():
    policy = json.loads((ROOT / "config" / "kos_social_publish_readiness_auditor_policy.json").read_text(encoding="utf-8-sig"))
    assert policy["creates_new_publish_executor"] is False
    assert policy["existing_publish_path_reused"] == "69D-69E-69F-69G-69H"
    assert policy["auto_publish_enabled"] is False
    assert policy["operator_review_required"] is True
