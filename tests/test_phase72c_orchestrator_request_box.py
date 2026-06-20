from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase72c_orchestrator_request_box.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase72c", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase72c_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_orchestrator_request_box_policy.json").exists()
    assert (ROOT / "docs" / "KOS_ORCHESTRATOR_REQUEST_BOX_V072C.md").exists()


def test_phase72c_routes_social_request_safely():
    mod = load_module()
    result = mod.process_request(
        request="criar campanha para Hupmix esta semana sem publicar automaticamente",
        request_id="test-72c-social",
    )
    assert result["status"] == "KOS_ORCHESTRATOR_REQUEST_REVIEW_READY"
    assert result["route"] == "social_publish"
    assert result["auto_publish_enabled"] is False
    assert result["auto_execution_enabled"] is False
    assert result["operator_review_required"] is True
    assert result["instagram_publish_executed"] is False
    assert result["real_action_executed"] is False


def test_phase72c_blocks_parada_request_for_review():
    mod = load_module()
    result = mod.process_request(
        request="publicar na paradaatlantida agora",
        request_id="test-72c-block",
    )
    assert result["status"] == "KOS_ORCHESTRATOR_REQUEST_BLOCKED_FOR_REVIEW"
    assert result["parada_atlantida_locked"] is True
    assert result["auto_execution_enabled"] is False
    assert result["instagram_publish_executed"] is False


def test_phase72c_policy_safe():
    policy = json.loads((ROOT / "config" / "kos_orchestrator_request_box_policy.json").read_text(encoding="utf-8-sig"))
    assert policy["purpose"] == "single_dialog_box_to_ask_the_orchestrator"
    assert policy["reuses_existing_modules"] is True
    assert policy["creates_new_publisher"] is False
    assert policy["creates_new_orchestrator"] is False
    assert policy["auto_execution_enabled"] is False
    assert policy["operator_review_required"] is True


def test_phase72c_cockpit_patched():
    page = (ROOT / "pages" / "KOS_Unified_Command_Cockpit.py").read_text(encoding="utf-8-sig")
    assert "KOS_PHASE72C_ORCHESTRATOR_REQUEST_BOX_START" in page
    assert "Pedido ao Orquestrador" in page
