from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_gmail_registry_exists():
    path = ROOT / "memory" / "kos_governance" / "KOS_GOOGLE_WORKSPACE_CONNECTION_REGISTRY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "KOS_GOOGLE_WORKSPACE_CONNECTION_REGISTRY_READY"
    assert data["official_google_project"]["project_id"] == "buoyant-song-491421-v6"
    assert data["official_google_project"]["oauth_app"] == "kaizen-home"
    assert data["gmail"]["capabilities"]["read"] is True
    assert data["gmail"]["capabilities"]["reports"] is True


def test_gmail_skill_exists():
    path = ROOT / "memory" / "kos_skills" / "KOS_SKILL_GMAIL_OPERATOR_V1.md"
    text = path.read_text(encoding="utf-8")
    assert "GMAIL OPERATOR" in text
    assert "SEND_GMAIL" in text
    assert "TRASH_GMAIL" in text
    assert "PERMANENT_DELETE_GMAIL" in text


def test_gmail_script_has_guardrails():
    path = ROOT / "scripts" / "run_gmail_operator.py"
    text = path.read_text(encoding="utf-8")
    assert "SEND_GMAIL" in text
    assert "TRASH_GMAIL" in text
    assert "PERMANENT_DELETE_GMAIL" in text
    assert "https://www.googleapis.com/auth/gmail.modify" in text
    assert "https://mail.google.com/" in text
