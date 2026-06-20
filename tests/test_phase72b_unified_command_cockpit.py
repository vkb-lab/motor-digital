from pathlib import Path
import json
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase72b_unified_command_cockpit_inventory.py"


def load_module():
    spec = importlib.util.spec_from_file_location("phase72b", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_phase72b_files_exist():
    assert SCRIPT.exists()
    assert (ROOT / "pages" / "KOS_Unified_Command_Cockpit.py").exists()
    assert (ROOT / "scripts" / "open_kos_unified_command_cockpit.ps1").exists()
    assert (ROOT / "config" / "kos_unified_command_cockpit_policy.json").exists()
    assert (ROOT / "docs" / "KOS_UNIFIED_COMMAND_COCKPIT_V072B.md").exists()


def test_phase72b_inventory_has_core_categories():
    mod = load_module()
    result = mod.build_inventory()
    assert result["status"] == "KOS_UNIFIED_COMMAND_COCKPIT_INVENTORY_READY"
    for key in ["runtime", "agents", "bridge", "products_saas", "social_publish", "patches", "dashboards"]:
        assert key in result["categories"]
    assert result["safe_flags"]["auto_publish_enabled"] is False
    assert result["safe_flags"]["operator_review_required"] is True
    assert result["safe_flags"]["parada_atlantida_locked"] is True


def test_phase72b_policy_safe_and_reuses_modules():
    policy = json.loads((ROOT / "config" / "kos_unified_command_cockpit_policy.json").read_text(encoding="utf-8-sig"))
    assert policy["reuses_existing_modules"] is True
    assert policy["creates_new_publisher"] is False
    assert policy["creates_new_orchestrator"] is False
    assert policy["auto_publish_enabled"] is False
    assert policy["auto_execution_enabled"] is False
    assert policy["operator_review_required"] is True


def test_phase72b_dashboard_contains_sections():
    page = (ROOT / "pages" / "KOS_Unified_Command_Cockpit.py").read_text(encoding="utf-8-sig")
    assert "Runtime e Agentes" in page
    assert "SaaS e Produtos" in page
    assert "Redes e Publicacoes" in page
    assert "Ponte ChatGPT" in page
    assert "Patch proposer" in page
    assert "nao publica" in page.lower() or "não publica" in page.lower()
