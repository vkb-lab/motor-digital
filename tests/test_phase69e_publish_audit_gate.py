from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase69e_publish_audit_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase69e_publish_audit", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase69e_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "config" / "kos_publish_audit_gate_policy.json").exists()
    assert (ROOT / "docs" / "KOS_PUBLISH_AUDIT_GATE_V069E.md").exists()


def test_phase69e_hupmix_audit_ready_and_does_not_publish():
    mod = load_module()
    audit = mod.build_publish_audit(
        campaign_id="TEST-69E",
        target="hupmix",
        channel="instagram",
        caption="Rascunho seguro para auditoria.",
        asset_ref="LOCAL_ASSET",
        operator_note="test",
        human_confirmed=False,
    )

    assert audit["status"] == "KOS_PUBLISH_AUDIT_PACKAGE_READY"
    assert audit["target"] == "hupmix"
    assert audit["publish_endpoint_called"] is False
    assert audit["http_post_used"] is False
    assert audit["instagram_publish_executed"] is False
    assert audit["browser_logged_account_automation_used"] is False
    assert audit["gates"]["instagram_publish_without_human_confirmation"]["allowed"] is False


def test_phase69e_blocks_parada_atlantida():
    mod = load_module()
    audit = mod.build_publish_audit(
        campaign_id="TEST-69E-BLOCK",
        target="paradaatlantida",
        channel="instagram",
        caption="bloquear",
        asset_ref="LOCAL_ASSET",
        operator_note="test",
        human_confirmed=True,
    )

    assert audit["status"] == "KOS_PUBLISH_AUDIT_BLOCKED"
    assert audit["reason"] == "blocked_target_parada_atlantida"
    assert audit["instagram_publish_executed"] is False


def test_phase69e_human_confirmed_still_does_not_publish():
    mod = load_module()
    audit = mod.build_publish_audit(
        campaign_id="TEST-69E-HUMAN",
        target="hupmix",
        channel="instagram",
        caption="Rascunho seguro com confirmacao humana para dry-run.",
        asset_ref="LOCAL_ASSET",
        operator_note="test",
        human_confirmed=True,
    )

    assert audit["eligible_for_human_confirmed_publish"] is True
    assert audit["publish_execution_command_generated"] is False
    assert audit["publish_endpoint_called"] is False
    assert audit["instagram_publish_executed"] is False
