from pathlib import Path
import json
from datetime import datetime, timezone

from k_atlas.ig_first_post import build_first_post_package, execute_first_post_if_armed
from k_atlas.ig_final_run.final_gate import inspect_phase14_gate

ROOT = Path(__file__).resolve().parents[2]
FINAL_TYPED_CONFIRMATION = "YES_I_CONFIRM_POST"

def _write_report(path_name: str, data: dict):
    path = ROOT / "reports" / path_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    data["path"] = str(path)
    return data

def build_phase14_final_package(
    client_id: str = "parada_atlantida",
    campaign_name: str = "campanha_lancamento_parada_atlantida",
    image_url: str = "https://placehold.co/1080x1080/png",
    caption: str = "Primeiro teste controlado preparado pelo K-OS.",
    load_runtime: bool = True
):
    first_post_package = build_first_post_package(client_id, campaign_name, image_url, caption)
    gate = inspect_phase14_gate(load_runtime=load_runtime)

    package = {
        "status": "READY_FOR_REAL_SEND" if gate["ready_for_real_send"] else "WAITING_FINAL_LOCKS",
        "client_id": client_id,
        "campaign_name": campaign_name,
        "image_url": image_url,
        "caption": caption,
        "gate": gate,
        "first_post_package": first_post_package,
        "required_typed_confirmation": FINAL_TYPED_CONFIRMATION,
        "real_action_executed": False,
        "external_call_executed": False,
        "manual_final_ok_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_report("KOS_PHASE14_IG_FINAL_PACKAGE.json", package)

def execute_phase14_if_confirmed(package: dict, typed_confirmation: str = "", execute_real_confirmed: bool = False):
    gate = inspect_phase14_gate(load_runtime=True)

    if not execute_real_confirmed:
        return _write_report("KOS_PHASE14_IG_FINAL_RESULT.json", {
            "status": "BLOCKED_BY_EXECUTE_SWITCH",
            "reason": "Parametro execute_real_confirmed ausente.",
            "gate": gate,
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    if typed_confirmation != FINAL_TYPED_CONFIRMATION:
        return _write_report("KOS_PHASE14_IG_FINAL_RESULT.json", {
            "status": "BLOCKED_BY_TYPED_CONFIRMATION",
            "reason": "Confirmacao digitada incorreta.",
            "expected": FINAL_TYPED_CONFIRMATION,
            "gate": gate,
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    if not gate["ready_for_real_send"]:
        return _write_report("KOS_PHASE14_IG_FINAL_RESULT.json", {
            "status": "BLOCKED_BY_PHASE14_GATE",
            "reason": "Travas finais ainda nao liberadas.",
            "gate": gate,
            "real_action_executed": False,
            "external_call_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    result = execute_first_post_if_armed(package["first_post_package"])

    final = {
        "status": result.get("status"),
        "result": result,
        "gate": gate,
        "real_action_executed": result.get("real_action_executed", False),
        "external_call_executed": result.get("external_call_executed", False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return _write_report("KOS_PHASE14_IG_FINAL_RESULT.json", final)

def run_phase14_final_check_demo():
    package = build_phase14_final_package(load_runtime=True)
    blocked = execute_phase14_if_confirmed(package, typed_confirmation="", execute_real_confirmed=False)

    demo = {
        "status": "PHASE14_FINAL_GATE_READY",
        "package": package,
        "blocked_result": blocked,
        "real_action_executed": False,
        "external_call_executed": False,
    }

    return _write_report("KOS_PHASE14_IG_FINAL_DEMO.json", demo)
