import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_router():
    path = ROOT / "scripts" / "run_phase72f_orchestrator_action_router.py"
    spec = importlib.util.spec_from_file_location("kos_router", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_instagram_connected_question_routes_to_account_status():
    router = load_router()
    assert router.detect_route("quais instagram estão conectados", {}) == "instagram_accounts_status"


def test_email_review_routes_to_email_ops():
    router = load_router()
    assert router.detect_route("revise meus emails", {}) == "email_ops"


def test_downloads_organize_routes_to_local_files():
    router = load_router()
    assert router.detect_route("organize meu computador downloads", {}) == "local_files_downloads"


def test_gmail_read_only_audit_script_exists():
    script = ROOT / "scripts" / "run_gmail_read_only_audit.py"
    text = script.read_text(encoding="utf-8")
    assert script.exists()
    assert "gmail.readonly" in text
    assert "email_sent" in text
    assert "email_deleted" in text


def test_orchestrator_consciousness_is_root_memory_and_packet_evidence():
    memory_doc = ROOT / "memory" / "kos_governance" / "KOS_ORCHESTRATOR_CONSCIOUSNESS_V1.md"
    report_doc = ROOT / "reports" / "KOS_ORCHESTRATOR_CONSCIOUSNESS_V1.md"
    assert memory_doc.exists()
    assert report_doc.exists()

    text = memory_doc.read_text(encoding="utf-8-sig")
    assert "Consciência Raiz do Orquestrador" in text
    assert "Human Gate" in text
    assert "Portal Atlântida" in text

    router = load_router()
    snapshot = router.consciousness_snapshot()
    assert snapshot["status"] == "KOS_ORCHESTRATOR_CONSCIOUSNESS_ACTIVE"
    assert snapshot["active"] is True
    assert "operating_cycle" in snapshot
