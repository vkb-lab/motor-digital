from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69h_hupmix_real_publish_executor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase69h_executor", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def ensure_ready_ledger():
    path = ROOT / "local_runtime" / "kos_publish_approval_ledger" / "hupmix" / "latest_publish_approval_ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "status": "KOS_REAL_PUBLISH_APPROVAL_LEDGER_CREATED",
        "campaign_id": "TEST-LEDGER",
        "target": "hupmix"
    }), encoding="utf-8")


def test_phase69h_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_hupmix_real_publish_executor_policy.json").exists()
    assert (ROOT / "docs" / "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_V069H.md").exists()


def test_phase69h_dry_run_ready_without_post():
    ensure_ready_ledger()
    mod = load_module()
    result = mod.build_executor_result(
        campaign_id="TEST-69H-DRY",
        target="hupmix",
        caption="Caption segura para dry-run.",
        image_url="https://example.com/test.jpg",
        operator="tester",
        confirmation="",
        execute_real_publish=False,
    )

    assert result["status"] == "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_READY_DRY_RUN"
    assert result["publish_endpoint_called"] is False
    assert result["http_post_used"] is False
    assert result["instagram_publish_executed"] is False


def test_phase69h_blocks_without_final_confirmation_when_execute_requested():
    ensure_ready_ledger()
    mod = load_module()
    result = mod.build_executor_result(
        campaign_id="TEST-69H-BLOCK",
        target="hupmix",
        caption="Caption segura.",
        image_url="https://example.com/test.jpg",
        operator="tester",
        confirmation="",
        execute_real_publish=True,
    )

    assert result["status"] == "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED"
    assert result["reason"] == "missing_or_invalid_final_confirmation"
    assert result["instagram_publish_executed"] is False


def test_phase69h_blocks_parada_even_with_confirmation():
    ensure_ready_ledger()
    mod = load_module()
    result = mod.build_executor_result(
        campaign_id="TEST-69H-PARADA",
        target="paradaatlantida",
        caption="Nao pode.",
        image_url="https://example.com/test.jpg",
        operator="tester",
        confirmation="YES_EXECUTE_REAL_HUPMIX_INSTAGRAM_PUBLISH_NOW",
        execute_real_publish=True,
    )

    assert result["status"] == "KOS_HUPMIX_REAL_PUBLISH_EXECUTOR_BLOCKED"
    assert result["reason"] == "blocked_target_parada_atlantida"
    assert result["instagram_publish_executed"] is False
