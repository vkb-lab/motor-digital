from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
PAGES = ROOT / "pages"


def read_app() -> str:
    return APP.read_text(encoding="utf-8-sig")


def test_app_exposes_operator_chat_as_primary_action():
    text = read_app()
    assert "Entrar no Operator Chat" in text
    assert "Frontdoor operacional do K-OS: intenção, roteamento, Gmail, Toolbelt, Brain, sequências e Human Gate." in text
    assert "pages/KOS_Operator_Chat.py" in text or "/KOS_Operator_Chat" in text


def test_app_declares_official_navigation_and_legacy_warning():
    text = read_app()
    assert "Navegação oficial K-OS" in text
    assert "páginas legadas" in text.lower() or "paginas legadas" in text.lower()
    assert "modo avançado" in text.lower() or "modo avancado" in text.lower()


def test_app_does_not_contain_secret_markers():
    text = read_app().lower()
    for marker in ["token_gmail", "client_secret", "access_token", "refresh_token"]:
        assert marker not in text


def test_pages_directory_was_not_moved_or_deleted():
    assert PAGES.exists()
    assert (PAGES / "KOS_Operator_Chat.py").exists()
    assert (PAGES / "KOS_Unified_Command_Cockpit.py").exists()

    text = read_app().lower()
    forbidden_mutators = ["shutil.move", "os.remove", "unlink(", "rmdir(", "removedirs("]
    for marker in forbidden_mutators:
        assert marker not in text
