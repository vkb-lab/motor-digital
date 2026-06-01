"""Filesystem paths and bootstrap helpers for K-Atlas OS."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT_DIR / "agents"
LIVE_DIR = ROOT_DIR / "live"
MEMORY_DIR = ROOT_DIR / "memory"
REPORTS_DIR = ROOT_DIR / "reports"
CAMPAIGNS_DIR = ROOT_DIR / "campaigns"
CONTENT_PACKS_DIR = ROOT_DIR / "content_packs"
LOGS_DIR = ROOT_DIR / "logs"
SCRIPTS_DIR = ROOT_DIR / "scripts"
TESTS_DIR = ROOT_DIR / "tests"
EVENTS_FILE = LOGS_DIR / "events.jsonl"

REQUIRED_DIRS = [
    AGENTS_DIR,
    ROOT_DIR / "k_atlas",
    LIVE_DIR,
    MEMORY_DIR,
    REPORTS_DIR,
    CAMPAIGNS_DIR,
    CONTENT_PACKS_DIR,
    LOGS_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
]


def ensure_dirs() -> list[Path]:
    """Create all operational directories and return them."""
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
    return REQUIRED_DIRS


def relative_to_root(path: Path) -> str:
    """Return a stable display path relative to the project root."""
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except ValueError:
        return str(path)

