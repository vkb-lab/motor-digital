from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase72a_weekly_operator_workspace.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase72a", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase72a_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "pages" / "KOS_Weekly_Operator_Workspace.py").exists()
    assert (ROOT / "config" / "kos_weekly_operator_workspace_policy.json").exists()
    assert (ROOT / "docs" / "KOS_WEEKLY_OPERATOR_WORKSPACE_V072A.md").exists()


def test_phase72a_workspace_safe_and_complete():
    mod = load_module()
    result = mod.build_week_workspace(week_id="test-week-72a")
    assert result["status"] == "KOS_WEEKLY_OPERATOR_WORKSPACE_READY"
    assert "admin" in result["tracks"]
    assert "saas" in result["tracks"]
    assert "social" in result["tracks"]
    assert len(result["days"]) == 7
    assert result["guardrails"]["auto_publish_enabled"] is False
    assert result["guardrails"]["auto_execution_enabled"] is False
    assert result["guardrails"]["operator_review_required"] is True
    assert result["guardrails"]["parada_atlantida_locked"] is True


def test_phase72a_policy_safe():
    policy = json.loads((ROOT / "config" / "kos_weekly_operator_workspace_policy.json").read_text(encoding="utf-8-sig"))
    assert policy["auto_publish_enabled"] is False
    assert policy["auto_execution_enabled"] is False
    assert policy["operator_review_required"] is True
    assert policy["parada_atlantida_locked"] is True
    assert policy["target_test_account"] == "hupmix"
