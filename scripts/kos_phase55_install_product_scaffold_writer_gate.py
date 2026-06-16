from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

ROOT = Path.cwd()

def now():
    return datetime.now(timezone.utc).isoformat()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

policy = {
    "status": "ACTIVE",
    "phase": "55",
    "module": "K-OS Product Scaffold Writer Gate",
    "mode": "HUMAN_GATE_DRY_RUN_ONLY",
    "goal": "criar gate humano para futura criacao local de scaffold sem criar arquivos reais agora",
    "required_confirmation_future": "YES_CREATE_PRODUCT_SCAFFOLD_LOCAL_ONLY",
    "blocked_actions": {
        "write_product_files_now": True,
        "build_product_automatically": True,
        "deploy_automatically": True,
        "instagram_publish": True,
        "paid_ai_call": True,
        "secret_exposure": True,
        "codex_auto_execute": True,
        "production_publish": True,
        "auto_commit": True,
        "auto_push": True
    },
    "hard_rules": {
        "dry_run_only": True,
        "gate_only": True,
        "no_file_creation": True,
        "human_approval_required_before_phase56": True,
        "no_paid_ai": True,
        "no_external_publish": True,
        "no_secret_exposure": True
    },
    "created_at": now()
}

gate_code = r'''
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
'''

runner_code = r'''
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from k_atlas.product_factory.mission_layer import create_product_mission
from k_atlas.product_factory.blueprint_generator import generate_blueprint_from_latest_mission
from k_atlas.product_factory.build_plan import generate_build_plan_from_latest_blueprint
from k_atlas.product_factory.scaffold_preview import generate_scaffold_preview_from_latest_build_plan
from k_atlas.product_factory.scaffold_writer_gate import generate_gate_from_latest_scaffold_preview, summarize_writer_gate

if __name__ == "__main__":
    create_product_mission(
        idea="Writer gate demo para SaaS K-OS Product Factory",
        product_type="saas",
        target_user="operador de pequenos negocios",
        market="automacao comercial com IA modular",
        priority="medium",
        source="phase55_runner"
    )

    generate_blueprint_from_latest_mission()
    generate_build_plan_from_latest_blueprint()
    generate_scaffold_preview_from_latest_build_plan()
    result = generate_gate_from_latest_scaffold_preview()

    print(json.dumps({
        "status": "PHASE55_PRODUCT_SCAFFOLD_WRITER_GATE_GENERATED",
        "result_status": result.get("status"),
        "gate_id": result.get("gate", {}).get("gate_id"),
        "files_count": result.get("gate", {}).get("files_count"),
        "write_product_files_allowed_now": False,
        "summary": summarize_writer_gate(),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False
    }, ensure_ascii=False, indent=2))
'''

page_code = r'''
import streamlit as st

from k_atlas.product_factory.scaffold_writer_gate import (
    get_latest_scaffold_preview,
    build_scaffold_writer_gate,
    evaluate_confirmation,
    save_gate_report,
    summarize_writer_gate,
    CONFIRMATION_PHRASE,
)

st.set_page_config(page_title="KOS Product Scaffold Writer Gate", layout="wide")

st.title("KOS Product Scaffold Writer Gate")
st.caption("Gate humano para futura criacao local de scaffold. Fase 55 nao cria arquivos reais.")

preview = get_latest_scaffold_preview()

if not preview:
    st.warning("Nenhum scaffold preview local encontrado.")
else:
    gate = build_scaffold_writer_gate(preview)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tipo", gate.get("product_type"))
    col2.metric("Arquivos", gate.get("files_count"))
    col3.metric("Criar arquivos", "BLOQUEADO")
    col4.metric("Deploy", "BLOQUEADO")

    st.subheader("Gate")
    st.json(gate)

    st.subheader("Confirmacao futura")
    st.code(CONFIRMATION_PHRASE)

    confirmation = st.text_input("Digite a confirmacao para avaliar dry-run", "")

    if st.button("Avaliar confirmacao sem criar arquivos", use_container_width=True):
        event = evaluate_confirmation(gate, confirmation)
        saved = save_gate_report(gate, event)
        st.json({"event": event, "saved": saved})

st.subheader("Resumo")
st.json(summarize_writer_gate())

st.warning("Gate-only. Nao cria arquivos reais, nao executa build, nao usa IA paga, nao publica.")
'''

test_code = r'''
from k_atlas.product_factory.mission_layer import build_product_mission
from k_atlas.product_factory.blueprint_generator import build_blueprint_from_mission
from k_atlas.product_factory.build_plan import build_plan_from_blueprint
from k_atlas.product_factory.scaffold_preview import build_scaffold_preview_from_build_plan
from k_atlas.product_factory.scaffold_writer_gate import (
    build_scaffold_writer_gate,
    evaluate_confirmation,
    CONFIRMATION_PHRASE,
)

def _preview():
    mission = build_product_mission(
        idea="SaaS teste gate",
        product_type="saas",
        target_user="cliente teste",
        market="mercado teste"
    )
    blueprint = build_blueprint_from_mission(mission)
    build_plan = build_plan_from_blueprint(blueprint)
    return build_scaffold_preview_from_build_plan(build_plan)

def test_writer_gate_is_safe_by_default():
    gate = build_scaffold_writer_gate(_preview())

    assert gate["status"] == "PRODUCT_SCAFFOLD_WRITER_GATE_READY"
    assert gate["gates"]["write_product_files_allowed"] is False
    assert gate["gates"]["create_directories_allowed"] is False
    assert gate["gates"]["build_allowed"] is False
    assert gate["gates"]["deploy_allowed"] is False
    assert gate["gates"]["paid_ai_allowed"] is False
    assert gate["real_action_executed"] is False
    assert gate["paid_ai_call_executed"] is False
    assert gate["instagram_publish_executed"] is False
    assert gate["external_side_effects_executed"] is False

def test_confirmation_valid_but_still_dry_run_only():
    gate = build_scaffold_writer_gate(_preview())
    result = evaluate_confirmation(gate, CONFIRMATION_PHRASE)

    assert result["confirmation_valid"] is True
    assert result["approved_for_future_phase56"] is True
    assert result["write_product_files_allowed_now"] is False
    assert result["phase55_still_dry_run_only"] is True
    assert result["real_action_executed"] is False

def test_confirmation_invalid():
    gate = build_scaffold_writer_gate(_preview())
    result = evaluate_confirmation(gate, "WRONG")

    assert result["confirmation_valid"] is False
    assert result["approved_for_future_phase56"] is False
    assert result["write_product_files_allowed_now"] is False
'''

save_json(ROOT / "config" / "kos_product_scaffold_writer_gate_policy.json", policy)
write(ROOT / "k_atlas" / "product_factory" / "scaffold_writer_gate.py", gate_code.strip() + "\n")

init_path = ROOT / "k_atlas" / "product_factory" / "__init__.py"
init_text = init_path.read_text(encoding="utf-8-sig") if init_path.exists() else ""
extra = "\nfrom .scaffold_writer_gate import build_scaffold_writer_gate, generate_gate_from_latest_scaffold_preview, summarize_writer_gate\n"
if "scaffold_writer_gate" not in init_text:
    init_path.write_text(init_text.rstrip() + extra, encoding="utf-8")

write(ROOT / "scripts" / "run_phase55_product_scaffold_writer_gate_demo.py", runner_code.strip() + "\n")
write(ROOT / "pages" / "KOS_Product_Scaffold_Writer_Gate.py", page_code.strip() + "\n")
write(ROOT / "tests" / "test_phase55_product_scaffold_writer_gate.py", test_code.strip() + "\n")

report = {
    "status": "PHASE55_PRODUCT_SCAFFOLD_WRITER_GATE_BOOTSTRAPPED",
    "phase": "55",
    "created_files": [
        "config/kos_product_scaffold_writer_gate_policy.json",
        "k_atlas/product_factory/scaffold_writer_gate.py",
        "scripts/run_phase55_product_scaffold_writer_gate_demo.py",
        "pages/KOS_Product_Scaffold_Writer_Gate.py",
        "tests/test_phase55_product_scaffold_writer_gate.py"
    ],
    "modified_files": [
        "k_atlas/product_factory/__init__.py"
    ],
    "runtime_files": [
        "local_runtime/product_factory_scaffold_writer_gate/latest_writer_gate.json",
        "local_runtime/product_factory_scaffold_writer_gate/writer_gate_events.jsonl"
    ],
    "real_action_executed": False,
    "paid_ai_call_executed": False,
    "instagram_publish_executed": False,
    "created_at": now()
}

save_json(ROOT / "reports" / "KOS_PHASE55_PRODUCT_SCAFFOLD_WRITER_GATE_BOOTSTRAP.json", report)
print(json.dumps(report, ensure_ascii=False, indent=2))