from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69f_human_confirmed_publish_dry_run_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase69f_dry_run", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase69f_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_human_confirmed_publish_dry_run_gate_policy.json").exists()
    assert (ROOT / "docs" / "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_GATE_V069F.md").exists()


def test_phase69f_blocks_without_confirmation():
    mod = load_module()
    result = mod.build_dry_run(
        campaign_id="TEST-69F-BLOCK",
        target="hupmix",
        channel="instagram",
        caption="Rascunho seguro.",
        asset_ref="LOCAL_ASSET",
        operator_note="test",
        confirmation="",
    )

    assert result["status"] == "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_BLOCKED"
    assert result["dry_run_package_ready"] is False
    assert result["instagram_publish_executed"] is False
    assert result["publish_endpoint_called"] is False


def test_phase69f_valid_confirmation_creates_dry_run_only():
    mod = load_module()
    result = mod.build_dry_run(
        campaign_id="TEST-69F-READY",
        target="hupmix",
        channel="instagram",
        caption="Rascunho seguro para dry-run.",
        asset_ref="LOCAL_ASSET",
        operator_note="test",
        confirmation="YES_DRY_RUN_HUPMIX_PUBLISH_AUDIT_ONLY",
    )

    assert result["status"] == "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_READY"
    assert result["dry_run_package_ready"] is True
    assert result["eligible_for_real_publish_future_gate"] is True
    assert result["publish_execution_command_generated"] is False
    assert result["publish_endpoint_called"] is False
    assert result["http_post_used"] is False
    assert result["instagram_publish_executed"] is False
    assert result["browser_logged_account_automation_used"] is False


def test_phase69f_parada_still_blocked_even_with_confirmation():
    mod = load_module()
    result = mod.build_dry_run(
        campaign_id="TEST-69F-PARADA",
        target="paradaatlantida",
        channel="instagram",
        caption="Nao pode.",
        asset_ref="LOCAL_ASSET",
        operator_note="test",
        confirmation="YES_DRY_RUN_HUPMIX_PUBLISH_AUDIT_ONLY",
    )

    assert result["status"] == "KOS_HUMAN_CONFIRMED_PUBLISH_DRY_RUN_BLOCKED"
    assert result["publish_audit"]["status"] == "KOS_PUBLISH_AUDIT_BLOCKED"
    assert result["instagram_publish_executed"] is False
