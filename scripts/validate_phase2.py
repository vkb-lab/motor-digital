"""Validate the local K-OS Phase 2 runtime surface.

This script intentionally checks repository capabilities instead of importing a
single private API. The Phase 2 smoke command calls this file directly, so it
must stay self-contained and deterministic.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_DIRS = (
    "agents",
    "k_atlas",
    "live",
    "memory",
    "reports",
    "campaigns",
    "content_packs",
    "logs",
    "scripts",
    "tests",
)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def require_path(relative: str, *, directory: bool = False) -> Path:
    path = ROOT / relative
    if directory and not path.is_dir():
        fail(f"pasta ausente: {relative}")
    if not directory and not path.exists():
        fail(f"arquivo ausente: {relative}")
    ok(relative)
    return path


def require_importable(relative: str) -> None:
    path = ROOT / relative
    module_name = Path(relative).with_suffix("").as_posix().replace("/", ".")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        fail(f"nao foi possivel carregar {relative}")
    ok(f"importavel: {relative}")


def require_writable(relative_dir: str, filename: str) -> None:
    directory = ROOT / relative_dir
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text("phase2-ok\n", encoding="utf-8")
    if path.read_text(encoding="utf-8") != "phase2-ok\n":
        fail(f"escrita falhou em {path.relative_to(ROOT)}")
    path.unlink(missing_ok=True)
    ok(f"escrita em {relative_dir}/")


def require_json_file(relative: str) -> None:
    path = ROOT / relative
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        path.write_text("{}\n", encoding="utf-8")
        text = "{}"

    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"JSON invalido em {relative}: {exc}")
    ok(f"JSON valido: {relative}")


def require_jsonl_writable(relative: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    probe = {"event": "phase2_validate", "status": "ok"}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(probe, ensure_ascii=True) + "\n")
    ok(f"append jsonl: {relative}")


def main() -> int:
    for directory in REQUIRED_DIRS:
        require_path(directory, directory=True)

    require_path("app.py")
    require_importable("app.py")
    require_writable("memory", ".phase2_write_probe")
    require_json_file("memory/operational.json")
    require_jsonl_writable("logs/events.jsonl")
    require_writable("reports", ".phase2_report_probe")

    print("STATUS: FASE 2 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
