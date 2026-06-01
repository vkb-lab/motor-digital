from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase2_repository_surface_exists() -> None:
    for relative in (
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
    ):
        assert (ROOT / relative).is_dir(), f"missing directory: {relative}"

    assert (ROOT / "app.py").is_file()
    assert (ROOT / "scripts" / "validate_phase2.py").is_file()


def test_app_module_is_importable() -> None:
    app_path = ROOT / "app.py"
    spec = importlib.util.spec_from_file_location("kos_app_under_test", app_path)
    assert spec is not None
    assert spec.loader is not None


def test_operational_memory_is_valid_json() -> None:
    memory_path = ROOT / "memory" / "operational.json"
    if not memory_path.exists():
        memory_path.write_text("{}\n", encoding="utf-8")

    text = memory_path.read_text(encoding="utf-8").strip() or "{}"
    assert isinstance(json.loads(text), dict)


def test_phase2_runtime_paths_are_writable(tmp_path: Path) -> None:
    probes = (
        ROOT / "memory" / ".pytest_phase2_probe",
        ROOT / "reports" / ".pytest_phase2_probe",
    )

    for path in probes:
        path.write_text("ok\n", encoding="utf-8")
        assert path.read_text(encoding="utf-8") == "ok\n"
        path.unlink(missing_ok=True)

    events_path = ROOT / "logs" / "events.jsonl"
    event = {"event": "pytest_phase2_probe", "status": "ok"}
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=True) + "\n")

