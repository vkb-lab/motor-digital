# -*- coding: utf-8 -*-
"""
K-OS Schema Guard
Checkpoint 016

Objetivo:
- validar JSONs operacionais antes de uso em gates, diagnosticos e propostas
- impedir que saidas quebradas de IA travem o K-OS
- gerar evidencia de auditoria
- nao chamar API externa
- nao enviar nada
- nao publicar nada
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()

REPORT_DIR = ROOT / "reports" / "schema"
MEMORY_DIR = ROOT / "memory" / "schema_guard"

LATEST_JSON = REPORT_DIR / "latest_schema_guard_report.json"
LATEST_MD = REPORT_DIR / "latest_schema_guard_report.md"
EVENTS_JSONL = MEMORY_DIR / "events.jsonl"

ALLOWED_DECISIONS = {
    "approved_local_only",
    "approved_for_local_diagnostic",
    "pending_review",
    "rejected",
}

ALLOWED_IMPACTS = {"baixo", "medio", "alto"}
ALLOWED_EFFORTS = {"baixo", "medio", "alto"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def error(code: str, message: str, field: str = "", severity: str = "high") -> dict[str, Any]:
    return {
        "code": code,
        "field": field,
        "message": message,
        "severity": severity,
    }


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def require_fields(data: dict[str, Any], fields: list[str]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    for field in fields:
        if field not in data:
            errors.append(error("missing_required_field", f"Campo obrigatorio ausente: {field}", field))

    return errors


def require_string(data: dict[str, Any], field: str, required: bool = True) -> list[dict[str, Any]]:
    if field not in data:
        return [error("missing_required_field", f"Campo obrigatorio ausente: {field}", field)] if required else []

    if not is_nonempty_string(data.get(field)):
        return [error("invalid_string", f"Campo deve ser string nao vazia: {field}", field)]

    return []


def require_bool(data: dict[str, Any], field: str, required: bool = True) -> list[dict[str, Any]]:
    if field not in data:
        return [error("missing_required_field", f"Campo obrigatorio ausente: {field}", field)] if required else []

    if not is_bool(data.get(field)):
        return [error("invalid_bool", f"Campo deve ser booleano: {field}", field)]

    return []


def require_false(data: dict[str, Any], field: str, required: bool = False) -> list[dict[str, Any]]:
    if field not in data:
        return [error("missing_required_field", f"Campo obrigatorio ausente: {field}", field)] if required else []

    if data.get(field) is not False:
        return [error("unsafe_external_flag", f"Campo deve ser false: {field}", field, "critical")]

    return []


def validate_recommendations(items: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    if not isinstance(items, list):
        return [error("invalid_recommendations", "recommendations deve ser lista", "recommendations")]

    if len(items) == 0:
        errors.append(error("empty_recommendations", "recommendations nao pode ser vazio", "recommendations"))

    for index, item in enumerate(items):
        prefix = f"recommendations[{index}]"

        if not isinstance(item, dict):
            errors.append(error("invalid_recommendation_item", "item deve ser objeto", prefix))
            continue

        for field in ["name", "description", "impact", "effort"]:
            errors.extend(require_string(item, field))

        impact = str(item.get("impact", "")).lower()
        effort = str(item.get("effort", "")).lower()

        if impact and impact not in ALLOWED_IMPACTS:
            errors.append(error("invalid_impact", "impact deve ser baixo, medio ou alto", f"{prefix}.impact"))

        if effort and effort not in ALLOWED_EFFORTS:
            errors.append(error("invalid_effort", "effort deve ser baixo, medio ou alto", f"{prefix}.effort"))

    return errors


def validate_lead(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return [error("invalid_root", "lead deve ser objeto")]

    errors: list[dict[str, Any]] = []

    for field in ["lead_id", "created_at", "source", "status"]:
        errors.extend(require_string(data, field))

    errors.extend(require_false(data, "external_send_enabled", required=True))
    errors.extend(require_bool(data, "human_review_required", required=True))

    return errors


def validate_diagnostic(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return [error("invalid_root", "diagnostico deve ser objeto")]

    errors: list[dict[str, Any]] = []

    for field in ["diagnostic_id", "created_at", "source", "lead_id"]:
        errors.extend(require_string(data, field, required=(field != "lead_id")))

    errors.extend(require_bool(data, "ok", required=True))
    errors.extend(require_false(data, "external_send_enabled", required=True))
    errors.extend(require_bool(data, "human_review_required", required=True))
    errors.extend(validate_recommendations(data.get("recommendations")))

    return errors


def validate_offer(offer: Any) -> list[dict[str, Any]]:
    if not isinstance(offer, dict):
        return [error("invalid_offer", "offer deve ser objeto", "offer")]

    errors: list[dict[str, Any]] = []

    for field in ["name"]:
        errors.extend(require_string(offer, field))

    deliverables = offer.get("deliverables")
    if not isinstance(deliverables, list) or not deliverables:
        errors.append(error("invalid_deliverables", "offer.deliverables deve ser lista nao vazia", "offer.deliverables"))
    else:
        for index, item in enumerate(deliverables):
            if not is_nonempty_string(item):
                errors.append(error("invalid_deliverable", "entregavel deve ser string nao vazia", f"offer.deliverables[{index}]"))

    return errors


def validate_proposal(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return [error("invalid_root", "proposta deve ser objeto")]

    errors: list[dict[str, Any]] = []

    for field in ["proposal_id", "created_at", "source", "title"]:
        errors.extend(require_string(data, field, required=(field != "title")))

    errors.extend(require_bool(data, "ok", required=True))
    errors.extend(require_false(data, "external_send_enabled", required=True))
    errors.extend(require_bool(data, "human_review_required", required=True))
    errors.extend(validate_offer(data.get("offer")))
    errors.extend(validate_recommendations(data.get("recommended_automations")))

    return errors


def validate_gate_decision(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return [error("invalid_root", "decisao deve ser objeto")]

    errors: list[dict[str, Any]] = []

    errors.extend(require_bool(data, "ok", required=True))
    errors.extend(require_string(data, "decision", required=True))
    errors.extend(require_false(data, "external_send_enabled", required=True))

    decision = str(data.get("decision", "")).strip()
    if decision and decision not in ALLOWED_DECISIONS:
        errors.append(error("invalid_decision", "decision fora da allowlist", "decision"))

    if "human_approval_recorded" in data:
        errors.extend(require_bool(data, "human_approval_recorded", required=True))

    if "manual_send_required" in data:
        errors.extend(require_bool(data, "manual_send_required", required=True))

    return errors


def validate_instagram_posts(data: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    if not isinstance(data, list):
        return [error("invalid_root", "posts de Instagram devem ser lista")]

    if not data:
        errors.append(error("empty_posts", "lista de posts nao pode ser vazia"))

    for index, post in enumerate(data):
        prefix = f"posts[{index}]"

        if not isinstance(post, dict):
            errors.append(error("invalid_post", "post deve ser objeto", prefix))
            continue

        for field in ["title", "caption"]:
            errors.extend(require_string(post, field))

        hashtags = post.get("hashtags")
        if not isinstance(hashtags, list):
            errors.append(error("invalid_hashtags", "hashtags deve ser lista", f"{prefix}.hashtags"))
        else:
            for tag_index, tag in enumerate(hashtags):
                if not is_nonempty_string(tag):
                    errors.append(error("invalid_hashtag", "hashtag deve ser string nao vazia", f"{prefix}.hashtags[{tag_index}]"))

    return errors


def validate_generic_json(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return [error("invalid_json", "JSON vazio ou nulo")]

    return []


VALIDATORS = {
    "lead_v1": validate_lead,
    "public_capture_v1": validate_lead,
    "diagnostic_v1": validate_diagnostic,
    "proposal_v1": validate_proposal,
    "gate_decision_v1": validate_gate_decision,
    "instagram_posts_v1": validate_instagram_posts,
    "generic_json_v1": validate_generic_json,
}


def detect_schema(path: Path, data: Any) -> str:
    name = path.name.lower()
    full = safe_path(path).lower()

    if "instagram_posts" in name:
        return "instagram_posts_v1"

    if "diagnostic" in name or "diagnostico" in name:
        return "diagnostic_v1"

    if "proposal" in name or "proposta" in name:
        return "proposal_v1"

    if "approval" in name or "decision" in name or "gate" in name:
        return "gate_decision_v1"

    if "lead" in name or "capture" in name or "intake" in full:
        return "lead_v1"

    if isinstance(data, list) and data and isinstance(data[0], dict) and "caption" in data[0]:
        return "instagram_posts_v1"

    return "generic_json_v1"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[Any]:
    rows: list[Any] = []

    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip().lstrip("\ufeff")
        if not line:
            continue
        rows.append(json.loads(line))

    return rows


def validate_payload(schema: str, data: Any) -> dict[str, Any]:
    validator = VALIDATORS.get(schema)

    if not validator:
        errors = [error("unknown_schema", f"Schema desconhecido: {schema}", "schema", "critical")]
    else:
        errors = validator(data)

    blocking = [item for item in errors if item.get("severity") in {"critical", "high"}]

    return {
        "ok": len(blocking) == 0,
        "schema": schema,
        "errors_count": len(errors),
        "blocking_errors_count": len(blocking),
        "errors": errors,
    }


def validate_file(path: Path, schema: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": safe_path(path),
        "exists": path.exists(),
        "ok": False,
        "schema": schema or "auto",
        "rows_validated": 0,
        "errors_count": 0,
        "blocking_errors_count": 0,
        "errors": [],
    }

    if not path.exists():
        result["errors"].append(error("file_missing", "Arquivo nao encontrado", "path"))
        result["errors_count"] = 1
        result["blocking_errors_count"] = 1
        return result

    try:
        if path.suffix.lower() == ".jsonl":
            rows = read_jsonl(path)
            row_results = []

            for index, row in enumerate(rows):
                row_schema = schema or detect_schema(path, row)
                validation = validate_payload(row_schema, row)
                row_results.append({
                    "row": index + 1,
                    "schema": row_schema,
                    "ok": validation["ok"],
                    "errors_count": validation["errors_count"],
                    "blocking_errors_count": validation["blocking_errors_count"],
                    "errors": validation["errors"],
                })

            errors_count = sum(item["errors_count"] for item in row_results)
            blocking_count = sum(item["blocking_errors_count"] for item in row_results)

            result.update({
                "ok": blocking_count == 0,
                "schema": schema or "auto_jsonl",
                "rows_validated": len(rows),
                "errors_count": errors_count,
                "blocking_errors_count": blocking_count,
                "row_results": row_results,
            })

            return result

        data = read_json(path)
        selected_schema = schema or detect_schema(path, data)
        validation = validate_payload(selected_schema, data)

        result.update({
            "ok": validation["ok"],
            "schema": selected_schema,
            "rows_validated": 1,
            "errors_count": validation["errors_count"],
            "blocking_errors_count": validation["blocking_errors_count"],
            "errors": validation["errors"],
        })

        return result

    except Exception as exc:
        result["errors"].append(error("json_parse_error", str(exc), "json", "critical"))
        result["errors_count"] = 1
        result["blocking_errors_count"] = 1
        return result


def local_targets() -> list[Path]:
    candidates = [
        ROOT / "content_packs" / "marketplace_ia" / "instagram_posts.json",
        ROOT / "content_packs" / "marketplace_ia" / "instagram_posts_v2.json",
        ROOT / "live" / "marketplace_ia" / "lead_intake.jsonl",
        ROOT / "live" / "marketplace_ia" / "public_capture_queue.jsonl",
        ROOT / "live" / "marketplace_ia" / "latest_lead_diagnostic.json",
        ROOT / "live" / "marketplace_ia" / "latest_public_lead_diagnostic.json",
        ROOT / "live" / "marketplace_ia" / "latest_commercial_proposal.json",
        ROOT / "live" / "marketplace_ia" / "latest_public_commercial_proposal.json",
        ROOT / "live" / "marketplace_ia" / "instagram_approval_decision.json",
        ROOT / "live" / "marketplace_ia" / "proposal_approval_decision.json",
        ROOT / "live" / "marketplace_ia" / "public_proposal_approval_decision.json",
    ]

    return [item for item in candidates if item.exists()]


def scan_local() -> dict[str, Any]:
    targets = local_targets()
    results = [validate_file(path) for path in targets]

    blocking = sum(item.get("blocking_errors_count", 0) for item in results)
    errors_total = sum(item.get("errors_count", 0) for item in results)

    return {
        "ok": blocking == 0,
        "checkpoint": "016",
        "module": "k_os_schema_guard",
        "status": "passed" if blocking == 0 else "blocked_by_schema",
        "generated_at": utc_now(),
        "targets_found": len(targets),
        "files_validated": len(results),
        "errors_count": errors_total,
        "blocking_errors_count": blocking,
        "results": results,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "manual_approval_required": True,
    }


def smoke_test() -> dict[str, Any]:
    valid_lead = {
        "lead_id": "lead_demo_001",
        "created_at": utc_now(),
        "source": "schema_guard_smoke",
        "status": "captured_local_only",
        "external_send_enabled": False,
        "human_review_required": True,
    }

    valid_diagnostic = {
        "ok": True,
        "diagnostic_id": "diag_demo_001",
        "created_at": utc_now(),
        "lead_id": "lead_demo_001",
        "source": "schema_guard_smoke",
        "external_send_enabled": False,
        "human_review_required": True,
        "recommendations": [
            {
                "name": "Dashboard operacional",
                "impact": "medio",
                "effort": "baixo",
                "description": "Centralizar status e proximos passos.",
            }
        ],
    }

    invalid_diagnostic = {
        "ok": True,
        "diagnostic_id": "diag_bad_001",
        "created_at": utc_now(),
        "source": "schema_guard_smoke",
        "external_send_enabled": True,
        "human_review_required": True,
        "recommendations": [],
    }

    valid_proposal = {
        "ok": True,
        "proposal_id": "proposal_demo_001",
        "created_at": utc_now(),
        "source": "schema_guard_smoke",
        "external_send_enabled": False,
        "human_review_required": True,
        "title": "Proposta Demo",
        "offer": {
            "name": "Plano IA Aplicada Starter",
            "deliverables": ["Diagnostico", "Primeira automacao"],
        },
        "recommended_automations": [
            {
                "name": "Follow-up assistido",
                "impact": "alto",
                "effort": "medio",
                "description": "Acompanhar oportunidades comerciais.",
            }
        ],
    }

    checks = [
        {
            "name": "valid_lead",
            "expected_ok": True,
            "result": validate_payload("lead_v1", valid_lead),
        },
        {
            "name": "valid_diagnostic",
            "expected_ok": True,
            "result": validate_payload("diagnostic_v1", valid_diagnostic),
        },
        {
            "name": "invalid_diagnostic_external_flag",
            "expected_ok": False,
            "result": validate_payload("diagnostic_v1", invalid_diagnostic),
        },
        {
            "name": "valid_proposal",
            "expected_ok": True,
            "result": validate_payload("proposal_v1", valid_proposal),
        },
    ]

    ok = all(item["result"]["ok"] == item["expected_ok"] for item in checks)

    return {
        "ok": ok,
        "checkpoint": "016",
        "module": "k_os_schema_guard",
        "status": "smoke_passed" if ok else "smoke_failed",
        "generated_at": utc_now(),
        "checks": checks,
        "external_send_enabled": False,
        "external_publish_enabled": False,
        "manual_approval_required": True,
    }


def write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# K-OS Schema Guard Report",
        "",
        f"- Checkpoint: {report.get('checkpoint')}",
        f"- Module: {report.get('module')}",
        f"- Status: {report.get('status')}",
        f"- OK: {report.get('ok')}",
        f"- Generated at: {report.get('generated_at')}",
        f"- Errors: {report.get('errors_count', 0)}",
        f"- Blocking errors: {report.get('blocking_errors_count', 0)}",
        "",
        "## Results",
        "",
    ]

    for item in report.get("results", []):
        lines.append(
            f"- {item.get('path')} | schema={item.get('schema')} | ok={item.get('ok')} | errors={item.get('errors_count')}"
        )

    if not report.get("results"):
        lines.append("- Nenhum arquivo operacional encontrado para scan local ou modo smoke test executado.")

    LATEST_MD.write_text("\n".join(lines), encoding="utf-8")

    event = {
        "event": "schema_guard.report_written",
        "created_at": utc_now(),
        "status": report.get("status"),
        "ok": report.get("ok"),
        "blocking_errors_count": report.get("blocking_errors_count", 0),
    }

    with EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke-test", "scan-local", "validate-file"], required=True)
    parser.add_argument("--path", default="")
    parser.add_argument("--schema", default="")
    args = parser.parse_args()

    if args.mode == "smoke-test":
        report = smoke_test()
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 3

    if args.mode == "scan-local":
        report = scan_local()
        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2

    if args.mode == "validate-file":
        if not args.path:
            raise SystemExit("Informe --path")

        path = ROOT / args.path
        result = validate_file(path, schema=args.schema or None)
        report = {
            "ok": result["ok"],
            "checkpoint": "016",
            "module": "k_os_schema_guard",
            "status": "passed" if result["ok"] else "blocked_by_schema",
            "generated_at": utc_now(),
            "results": [result],
            "errors_count": result["errors_count"],
            "blocking_errors_count": result["blocking_errors_count"],
            "external_send_enabled": False,
            "external_publish_enabled": False,
            "manual_approval_required": True,
        }

        write_report(report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())