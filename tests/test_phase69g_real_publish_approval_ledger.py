from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69g_real_publish_approval_ledger.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase69g_ledger", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def ensure_ready_dry_run():
    path = ROOT / "local_runtime" / "kos_publish_dry_run" / "hupmix" / "latest_publish_dry_run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "status": "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_READY",
        "campaign_id": "TEST-DRY-RUN",
        "target": "hupmix"
    }), encoding="utf-8")


def test_phase69g_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_real_publish_approval_ledger_policy.json").exists()
    assert (ROOT / "docs" / "KOS_REAL_PUBLISH_APPROVAL_LEDGER_V069G.md").exists()


def test_phase69g_blocks_without_approval_phrase():
    ensure_ready_dry_run()
    mod = load_module()
    result = mod.build_approval_ledger(
        campaign_id="TEST-69G-BLOCK",
        target="hupmix",
        caption="Rascunho.",
        asset_ref="LOCAL_ASSET",
        operator="tester",
        approval_phrase="",
        note="test",
    )

    assert result["status"] == "KOS_REAL_PUBLISH_APPROVAL_LEDGER_BLOCKED"
    assert result["approval_ledger_created"] is False
    assert result["instagram_publish_executed"] is False
    assert result["publish_endpoint_called"] is False


def test_phase69g_creates_ledger_without_publishing():
    ensure_ready_dry_run()
    mod = load_module()
    result = mod.build_approval_ledger(
        campaign_id="TEST-69G-READY",
        target="hupmix",
        caption="Rascunho aprovado para ledger.",
        asset_ref="LOCAL_ASSET",
        operator="tester",
        approval_phrase="YES_CREATE_HUPMIX_REAL_PUBLISH_APPROVAL_LEDGER_ONLY",
        note="test",
    )

    assert result["status"] == "KOS_REAL_PUBLISH_APPROVAL_LEDGER_CREATED"
    assert result["approval_ledger_created"] is True
    assert result["eligible_for_future_real_publish_executor"] is True
    assert result["publish_execution_command_generated"] is False
    assert result["publish_endpoint_called"] is False
    assert result["http_post_used"] is False
    assert result["instagram_publish_executed"] is False
    assert result["browser_logged_account_automation_used"] is False


def test_phase69g_blocks_parada_atlantida():
    ensure_ready_dry_run()
    mod = load_module()
    result = mod.build_approval_ledger(
        campaign_id="TEST-69G-PARADA",
        target="paradaatlantida",
        caption="Nao pode.",
        asset_ref="LOCAL_ASSET",
        operator="tester",
        approval_phrase="YES_CREATE_HUPMIX_REAL_PUBLISH_APPROVAL_LEDGER_ONLY",
        note="test",
    )

    assert result["status"] == "KOS_REAL_PUBLISH_APPROVAL_LEDGER_BLOCKED"
    assert result["reason"] == "blocked_target_parada_atlantida"
    assert result["instagram_publish_executed"] is False
