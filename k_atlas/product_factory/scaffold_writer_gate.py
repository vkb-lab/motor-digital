from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD_INDEX = ROOT / "local_runtime" / "product_factory_scaffolds" / "scaffold_previews_index.jsonl"
GATE_DIR = ROOT / "local_runtime" / "product_factory_scaffold_writer_gate"
LATEST_GATE = GATE_DIR / "latest_writer_gate.json"
GATE_EVENTS = GATE_DIR / "writer_gate_events.jsonl"

CONFIRMATION_PHRASE = "YES_CREATE_PRODUCT_SCAFFOLD_LOCAL_ONLY"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []

    items = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            pass
    return items

def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def get_latest_scaffold_preview() -> dict:
    index = _read_jsonl(SCAFFOLD_INDEX)
    if not index:
        return {}

    latest = index[-1]
    path = latest.get("path")
    if not path:
        return {}

    return _read_json(ROOT / path)

def build_scaffold_writer_gate(scaffold_preview: dict) -> dict:
    files_preview = scaffold_preview.get("files_preview", []) or []
    directories_preview = scaffold_preview.get("directories_preview", []) or []

    gate = {
        "status": "PRODUCT_SCAFFOLD_WRITER_GATE_READY",
        "gate_id": "PFSWG-" + uuid.uuid4().hex[:12].upper(),
        "source_scaffold_preview_id": scaffold_preview.get("scaffold_preview_id"),
        "source_build_plan_id": scaffold_preview.get("source_build_plan_id"),
        "title": scaffold_preview.get("title"),
        "slug": scaffold_preview.get("slug"),
        "product_type": scaffold_preview.get("product_type"),
        "target_root": scaffold_preview.get("target_root"),
        "files_count": len(files_preview),
        "directories_count": len(directories_preview),
        "files_preview": files_preview,
        "directories_preview": directories_preview,
        "required_confirmation": CONFIRMATION_PHRASE,
        "phase55_mode": "GATE_ONLY",
        "phase56_required_for_file_creation": True,
        "approval_state": {
            "human_confirmation_valid": False,
            "approval_recorded": False,
            "approved_for_future_phase56": False
        },
        "gates": {
            "write_product_files_allowed": False,
            "create_directories_allowed": False,
            "build_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "codex_auto_execute_allowed": False,
            "external_publish_allowed": False,
            "human_approval_required": True
        },
        "safe_next_step": "Fase 56 podera criar scaffold local somente com confirmacao humana explicita.",
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    return gate

def evaluate_confirmation(gate: dict, confirmation: str) -> dict:
    valid = (confirmation or "").strip() == CONFIRMATION_PHRASE

    result = {
        "status": "PRODUCT_SCAFFOLD_WRITER_CONFIRMATION_EVALUATED",
        "gate_id": gate.get("gate_id"),
        "source_scaffold_preview_id": gate.get("source_scaffold_preview_id"),
        "confirmation_valid": valid,
        "approved_for_future_phase56": valid,
        "write_product_files_allowed_now": False,
        "phase55_still_dry_run_only": True,
        "message": "Confirmacao valida para preparar Fase 56." if valid else "Confirmacao ausente ou invalida.",
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    return result

def save_gate_report(gate: dict, event: dict | None = None) -> dict:
    GATE_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "status": "PRODUCT_SCAFFOLD_WRITER_GATE_SAVED",
        "gate": gate,
        "event": event or {},
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_GATE, payload)
    _append_jsonl(GATE_EVENTS, payload)

    return payload

def generate_gate_from_latest_scaffold_preview(confirmation: str = "") -> dict:
    preview = get_latest_scaffold_preview()

    if not preview:
        result = {
            "status": "NO_PRODUCT_SCAFFOLD_PREVIEW_FOUND",
            "message": "Nenhum scaffold preview encontrado no runtime local.",
            "real_action_executed": False,
            "paid_ai_call_executed": False,
            "instagram_publish_executed": False
        }
        save_gate_report(result)
        return result

    gate = build_scaffold_writer_gate(preview)
    event = evaluate_confirmation(gate, confirmation)
    saved = save_gate_report(gate, event)

    return {
        "status": "PRODUCT_SCAFFOLD_WRITER_GATE_GENERATED",
        "gate": gate,
        "confirmation_event": event,
        "saved": saved.get("status"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False
    }

def summarize_writer_gate() -> dict:
    latest = _read_json(LATEST_GATE)
    events = _read_jsonl(GATE_EVENTS)[-10:]

    return {
        "status": "PRODUCT_SCAFFOLD_WRITER_GATE_SUMMARY_READY",
        "latest_gate_exists": LATEST_GATE.exists(),
        "events_count": len(events),
        "latest": latest,
        "last_events": events,
        "write_product_files_allowed_now": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

if __name__ == "__main__":
    print(json.dumps(generate_gate_from_latest_scaffold_preview(), ensure_ascii=False, indent=2))
