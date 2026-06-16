from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from k_atlas.product_factory.product_registry import refresh_product_registry, get_latest_registry

ROOT = Path(__file__).resolve().parents[2]
QA_DIR = ROOT / "local_runtime" / "product_qa_gate"
LATEST_REPORT = QA_DIR / "latest_product_qa_report.json"
EVENTS_PATH = QA_DIR / "product_qa_events.jsonl"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _append_jsonl(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"error": str(exc), "path": str(path)}

def _check(name: str, passed: bool, severity: str, message: str) -> dict:
    return {
        "name": name,
        "passed": bool(passed),
        "severity": severity,
        "message": message,
    }

def evaluate_product_record(product: dict) -> dict:
    suspicious_files = product.get("suspicious_files", []) or []

    checks = [
        _check(
            "readme_present",
            product.get("has_readme") is True,
            "medium",
            "Produto deve possuir README.md com instrucoes locais."
        ),
        _check(
            "policy_present",
            product.get("has_policy") is True,
            "high",
            "Produto deve possuir config/product_policy.json."
        ),
        _check(
            "tests_present",
            product.get("has_tests") is True,
            "medium",
            "Produto deve possuir pasta tests/."
        ),
        _check(
            "no_suspicious_files",
            product.get("safe") is True and len(suspicious_files) == 0,
            "critical",
            "Produto nao deve conter .env, tokens, credentials ou arquivos sensiveis."
        ),
        _check(
            "execution_blocked",
            product.get("execution_allowed") is False,
            "high",
            "Execucao automatica deve permanecer bloqueada."
        ),
        _check(
            "deploy_blocked",
            product.get("deploy_allowed") is False,
            "high",
            "Deploy deve permanecer bloqueado."
        ),
        _check(
            "paid_ai_blocked",
            product.get("paid_ai_allowed") is False,
            "high",
            "IA paga deve permanecer bloqueada."
        ),
        _check(
            "instagram_blocked",
            product.get("instagram_publish_allowed") is False,
            "high",
            "Instagram/publicacao social deve permanecer bloqueado."
        ),
        _check(
            "external_publish_blocked",
            product.get("external_publish_allowed") is False,
            "high",
            "Publicacao externa deve permanecer bloqueada."
        ),
        _check(
            "reversible_structure",
            product.get("has_readme") is True and product.get("has_policy") is True,
            "medium",
            "Produto deve ser reversivel e compreensivel por README + policy."
        ),
        _check(
            "local_instructions_clear",
            product.get("has_readme") is True,
            "low",
            "Produto deve ter instrucoes locais claras."
        ),
    ]

    failed = [item for item in checks if item["passed"] is not True]
    critical_failed = [item for item in failed if item["severity"] == "critical"]
    high_failed = [item for item in failed if item["severity"] == "high"]

    if critical_failed:
        qa_status = "PRODUCT_QA_CRITICAL"
    elif high_failed or failed:
        qa_status = "PRODUCT_QA_ATTENTION_REQUIRED"
    else:
        qa_status = "PRODUCT_QA_PASS"

    score = int(round((len(checks) - len(failed)) / len(checks) * 100)) if checks else 0

    return {
        "status": qa_status,
        "product_id": product.get("product_id"),
        "slug": product.get("slug"),
        "title": product.get("title"),
        "product_type": product.get("product_type"),
        "path": product.get("path"),
        "score": score,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "critical_failed_count": len(critical_failed),
        "high_failed_count": len(high_failed),
        "checks": checks,
        "suspicious_files": suspicious_files,
        "human_review_required": qa_status != "PRODUCT_QA_PASS",
        "execution_allowed": False,
        "deploy_allowed": False,
        "paid_ai_allowed": False,
        "instagram_publish_allowed": False,
        "external_publish_allowed": False,
        "auto_fix_allowed": False,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def build_product_qa_report(registry_payload: dict) -> dict:
    snapshot = registry_payload.get("snapshot", registry_payload)
    products = snapshot.get("products", []) or []
    qa_items = [evaluate_product_record(item) for item in products]

    passed = [item for item in qa_items if item.get("status") == "PRODUCT_QA_PASS"]
    attention = [item for item in qa_items if item.get("status") == "PRODUCT_QA_ATTENTION_REQUIRED"]
    critical = [item for item in qa_items if item.get("status") == "PRODUCT_QA_CRITICAL"]

    if critical:
        overall = "PRODUCT_QA_GATE_CRITICAL"
    elif attention:
        overall = "PRODUCT_QA_GATE_ATTENTION_REQUIRED"
    else:
        overall = "PRODUCT_QA_GATE_PASS"

    return {
        "status": overall,
        "products_count": len(qa_items),
        "passed_count": len(passed),
        "attention_required_count": len(attention),
        "critical_count": len(critical),
        "qa_items": qa_items,
        "gates": {
            "read_only": True,
            "product_execution_allowed": False,
            "auto_fix_allowed": False,
            "file_deletion_allowed": False,
            "deploy_allowed": False,
            "paid_ai_allowed": False,
            "instagram_publish_allowed": False,
            "external_publish_allowed": False,
            "human_review_required": len(attention) > 0 or len(critical) > 0
        },
        "recommendations": [
            "Adicionar README.md quando ausente.",
            "Adicionar config/product_policy.json quando ausente.",
            "Adicionar testes em products/<slug>/tests quando ausentes.",
            "Remover arquivos sensiveis do produto antes de qualquer evolucao.",
            "Manter execucao, deploy, IA paga e publicacao externa bloqueados ate revisao humana."
        ],
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def save_product_qa_report(report: dict) -> dict:
    payload = {
        "status": "PRODUCT_QA_GATE_REPORT_SAVED",
        "report": report,
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

    _write_json(LATEST_REPORT, payload)
    _append_jsonl(EVENTS_PATH, payload)
    return payload

def refresh_product_qa_gate() -> dict:
    refresh_product_registry()
    registry = get_latest_registry()
    report = build_product_qa_report(registry)
    saved = save_product_qa_report(report)

    return {
        "status": "PRODUCT_QA_GATE_REFRESHED",
        "qa_status": report.get("status"),
        "products_count": report.get("products_count", 0),
        "passed_count": report.get("passed_count", 0),
        "attention_required_count": report.get("attention_required_count", 0),
        "critical_count": report.get("critical_count", 0),
        "saved": saved.get("status"),
        "qa_report_path": str(LATEST_REPORT.relative_to(ROOT)).replace("\\", "/"),
        "real_action_executed": False,
        "paid_ai_call_executed": False,
        "instagram_publish_executed": False,
        "external_side_effects_executed": False,
        "created_at": now()
    }

def get_latest_product_qa_report() -> dict:
    if LATEST_REPORT.exists():
        return _read_json(LATEST_REPORT)
    return save_product_qa_report(build_product_qa_report(get_latest_registry()))

if __name__ == "__main__":
    print(json.dumps(refresh_product_qa_gate(), ensure_ascii=False, indent=2))