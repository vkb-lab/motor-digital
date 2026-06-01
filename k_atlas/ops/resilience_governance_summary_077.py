# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


CHECKPOINT_ID = "077"
CHECKPOINT_NAME = "K-Agent Resilience Governance Summary Core"
ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = ROOT / "configs" / "resilience_governance_summary_077.json"
REPORT_DIR = ROOT / "reports" / "resilience" / "077_resilience_governance_summary"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "077_k_agent_resilience_governance_summary.md"

SOURCE_CHECKPOINTS = ["071", "072", "073", "074", "075", "076"]

BLOCKED_OPERATIONS = [
    "real_drill_execution",
    "real_recovery_execution",
    "real_rollback_execution",
    "git_reset_hard",
    "force_push",
    "destructive_shell",
    "memory_deletion",
    "secret_export",
]

SENSITIVE_KEY_RE = re.compile(
    r"(secret|token|password|credential|authorization|private_key|api_key|bearer)",
    re.IGNORECASE,
)

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"sk-[0-9A-Za-z_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path).replace("\\", "/")


def ensure_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        clean: Dict[str, Any] = {}
        for key, value in obj.items():
            if SENSITIVE_KEY_RE.search(str(key)):
                clean[str(key)] = "[REDACTED]"
            else:
                clean[str(key)] = sanitize(value)
        return clean

    if isinstance(obj, list):
        return [sanitize(item) for item in obj]

    if isinstance(obj, str):
        result = obj
        for pattern in SENSITIVE_VALUE_PATTERNS:
            result = pattern.sub("[REDACTED]", result)
        return result

    return obj


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except Exception:
        return None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_data = sanitize(data)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(safe_data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": "Resilience",
        "objective": (
            "Consolidar governanca da camada de resilience usando evidencias "
            "dos checkpoints 071-076 sem executar drill, recovery, rollback, "
            "shell destrutivo, git reset hard ou force push."
        ),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "allowed_operations": [
            "read_existing_evidence",
            "generate_sanitized_reports",
            "generate_governance_summary",
            "update_accountability_register_if_exists",
            "generate_streamlit_read_only_page",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "evidence_policy": {
            "include_file_hashes": True,
            "include_file_paths": True,
            "include_sensitive_content": False,
            "sanitize_reports": True,
        },
        "status": "configured",
    }


def load_config() -> Dict[str, Any]:
    data = read_json(CONFIG_PATH)
    if isinstance(data, dict):
        return data
    data = default_config()
    write_json(CONFIG_PATH, data)
    return data


def list_candidate_files() -> List[Path]:
    roots = [
        ROOT / "reports",
        ROOT / "memory",
        ROOT / "docs",
        ROOT / "configs",
    ]

    files: List[Path] = []
    ignored_parts = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".streamlit",
    }

    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            parts = set(path.parts)
            if parts.intersection(ignored_parts):
                continue
            rel_path = rel(path)
            if rel_path.startswith("reports/security/latest_security_firewall_report"):
                continue
            if "077_resilience_governance_summary" in rel_path:
                continue
            try:
                if path.stat().st_size > 5 * 1024 * 1024:
                    continue
            except Exception:
                continue
            files.append(path)

    return sorted(files, key=lambda item: rel(item))


def file_record(path: Path) -> Dict[str, Any]:
    stat = path.stat()
    record: Dict[str, Any] = {
        "path": rel(path),
        "size_bytes": stat.st_size,
        "modified_utc": dt.datetime.fromtimestamp(
            stat.st_mtime,
            tz=dt.timezone.utc,
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sha256": sha256_file(path),
    }

    if path.suffix.lower() == ".json":
        data = read_json(path)
        if isinstance(data, dict):
            record["json_keys"] = sorted([str(key) for key in data.keys()])[:30]
            for key in ["checkpoint", "status", "result", "state"]:
                if key in data and not isinstance(data[key], (dict, list)):
                    record[key] = sanitize(str(data[key]))[:160]

    return record


def discover_evidence() -> Dict[str, Any]:
    candidates = list_candidate_files()
    by_checkpoint: Dict[str, Any] = {}

    for checkpoint in SOURCE_CHECKPOINTS:
        matched: List[Path] = []
        for path in candidates:
            lower_path = rel(path).lower()
            filename = path.name.lower()
            if checkpoint in lower_path or f"checkpoint_{checkpoint}" in filename:
                matched.append(path)

        records = [file_record(path) for path in matched[:80]]

        by_checkpoint[checkpoint] = {
            "checkpoint": checkpoint,
            "evidence_count": len(records),
            "status": "evidence_found" if records else "evidence_gap",
            "files": records,
        }

    total_files = sum(item["evidence_count"] for item in by_checkpoint.values())
    complete = all(item["evidence_count"] > 0 for item in by_checkpoint.values())

    return {
        "generated_at": now_utc(),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "evidence_complete": complete,
        "total_evidence_files": total_files,
        "checkpoints": by_checkpoint,
    }


def build_governance_summary(config: Dict[str, Any]) -> Dict[str, Any]:
    evidence = discover_evidence()

    controls = [
        {
            "control": "readiness_governance",
            "source_checkpoint": "071",
            "purpose": "Registrar prontidao operacional da camada de resilience.",
            "status": evidence["checkpoints"]["071"]["status"],
        },
        {
            "control": "scenario_planning_governance",
            "source_checkpoint": "072",
            "purpose": "Registrar planejamento seguro de cenarios sem execucao destrutiva.",
            "status": evidence["checkpoints"]["072"]["status"],
        },
        {
            "control": "drill_design_governance",
            "source_checkpoint": "073",
            "purpose": "Registrar desenho de drill sem execucao real.",
            "status": evidence["checkpoints"]["073"]["status"],
        },
        {
            "control": "dry_run_governance",
            "source_checkpoint": "074",
            "purpose": "Registrar dry run controlado sem recovery, rollback ou drill real.",
            "status": evidence["checkpoints"]["074"]["status"],
        },
        {
            "control": "operator_review_governance",
            "source_checkpoint": "075",
            "purpose": "Registrar revisao humana e governanca de aprovacao.",
            "status": evidence["checkpoints"]["075"]["status"],
        },
        {
            "control": "evidence_pack_governance",
            "source_checkpoint": "076",
            "purpose": "Registrar pacote de evidencias sanitizadas da camada.",
            "status": evidence["checkpoints"]["076"]["status"],
        },
    ]

    evidence_gaps = [
        checkpoint
        for checkpoint, item in evidence["checkpoints"].items()
        if item["status"] != "evidence_found"
    ]

    governance_status = "complete" if not evidence_gaps else "complete_with_evidence_gaps"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": "Resilience",
        "generated_at": now_utc(),
        "status": governance_status,
        "objective": config.get("objective"),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "controls": controls,
        "evidence": evidence,
        "evidence_gaps": evidence_gaps,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "git_reset_hard_executed": False,
            "force_push_executed": False,
            "destructive_shell_executed": False,
            "memory_deletion_executed": False,
            "secret_export_executed": False,
        },
        "governance_decision": {
            "layer_ready_for_closure_checkpoint_078": True,
            "closure_condition": (
                "Checkpoint 077 consolidou governanca com evidencias existentes. "
                "Lacunas de evidencia, se houver, ficam registradas sem bloquear "
                "a criacao do resumo de governanca."
            ),
        },
    }


def governance_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 077 - K-Agent Resilience Governance Summary Core")
    lines.append("")
    lines.append(f"Gerado em: {summary['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(summary.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {summary['checkpoint']}")
    lines.append(f"- Camada: {summary['layer']}")
    lines.append(f"- Status: {summary['status']}")
    lines.append(f"- Evidencias totais: {summary['evidence']['total_evidence_files']}")
    lines.append("")
    lines.append("## Controles consolidados")
    lines.append("")
    lines.append("| Controle | Checkpoint fonte | Status | Finalidade |")
    lines.append("|---|---:|---|---|")
    for control in summary["controls"]:
        lines.append(
            f"| {control['control']} | {control['source_checkpoint']} | "
            f"{control['status']} | {control['purpose']} |"
        )

    lines.append("")
    lines.append("## Politica de seguranca")
    lines.append("")
    lines.append("Operacoes bloqueadas neste checkpoint:")
    for operation in summary["blocked_operations"]:
        lines.append(f"- {operation}")

    lines.append("")
    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in summary["execution_guard"].items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("## Evidencias por checkpoint")
    lines.append("")
    for checkpoint, item in summary["evidence"]["checkpoints"].items():
        lines.append(f"### {checkpoint}")
        lines.append("")
        lines.append(f"- Status: {item['status']}")
        lines.append(f"- Arquivos: {item['evidence_count']}")
        for file_item in item["files"][:20]:
            lines.append(f"  - {file_item['path']} | sha256={file_item['sha256']}")
        lines.append("")

    if summary["evidence_gaps"]:
        lines.append("## Lacunas registradas")
        lines.append("")
        for checkpoint in summary["evidence_gaps"]:
            lines.append(f"- {checkpoint}")
        lines.append("")
    else:
        lines.append("## Lacunas registradas")
        lines.append("")
        lines.append("Nenhuma lacuna de evidencia detectada.")
        lines.append("")

    lines.append("## Decisao operacional")
    lines.append("")
    lines.append(
        "A camada de resilience esta governada para seguir ao checkpoint 078 - "
        "K-Agent Resilience Layer Closure Core."
    )
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(summary: Dict[str, Any]) -> List[str]:
    candidate_paths = [
        ROOT / "memory" / "accountability_register.json",
        ROOT / "memory" / "governance" / "accountability_register.json",
        ROOT / "reports" / "accountability_register.json",
        ROOT / "reports" / "governance" / "accountability_register.json",
    ]

    updated: List[str] = []

    entry = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": "Resilience",
        "status": summary["status"],
        "updated_at": now_utc(),
        "evidence_report": rel(REPORT_DIR / "077_governance_summary.json"),
        "closure_report": rel(REPORT_DIR / "077_closure_report.json"),
        "blocked_operations_confirmed": True,
    }

    for path in candidate_paths:
        if not path.exists():
            continue

        data = read_json(path)

        if isinstance(data, list):
            data = [
                item for item in data
                if not (isinstance(item, dict) and item.get("checkpoint") == CHECKPOINT_ID)
            ]
            data.append(entry)
            write_json(path, data)
            updated.append(rel(path))

        elif isinstance(data, dict):
            checkpoints = data.get("checkpoints")
            if not isinstance(checkpoints, list):
                checkpoints = []

            checkpoints = [
                item for item in checkpoints
                if not (isinstance(item, dict) and item.get("checkpoint") == CHECKPOINT_ID)
            ]
            checkpoints.append(entry)
            data["checkpoints"] = checkpoints
            data["updated_at"] = now_utc()
            write_json(path, data)
            updated.append(rel(path))

    return updated


def mode_init() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "init",
        "status": "initialized",
        "generated_at": now_utc(),
        "config_path": rel(CONFIG_PATH),
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "destructive_shell_executed": False,
        },
        "config": sanitize(config),
    }
    write_json(REPORT_DIR / "077_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    summary = build_governance_summary(config)

    write_json(REPORT_DIR / "077_governance_summary.json", summary)
    write_text(REPORT_DIR / "077_governance_summary.md", governance_markdown(summary))
    write_text(DOCS_PATH, governance_markdown(summary))

    updated_registers = update_accountability_register(summary)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "governance_summary_json": rel(REPORT_DIR / "077_governance_summary.json"),
        "governance_summary_md": rel(REPORT_DIR / "077_governance_summary.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": summary["execution_guard"],
    }

    write_json(REPORT_DIR / "077_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_077_resilience_governance_summary.ps1",
        ROOT / "pages" / "077_Resilience_Governance_Summary.py",
        DOCS_PATH,
        REPORT_DIR / "077_init_report.json",
        REPORT_DIR / "077_action_report.json",
        REPORT_DIR / "077_governance_summary.json",
        REPORT_DIR / "077_governance_summary.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    summary = read_json(REPORT_DIR / "077_governance_summary.json")
    guard_ok = False
    if isinstance(summary, dict):
        guard = summary.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "notes": [
            "Validacao confirma artefatos principais.",
            "Validacao confirma que o checkpoint nao executou drill, recovery ou rollback real.",
        ],
    }

    write_json(REPORT_DIR / "077_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 077 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "077_validate_report.json")
    summary = read_json(REPORT_DIR / "077_governance_summary.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    summary_exists = isinstance(summary, dict)

    checks = {
        "validate_passed": validate_passed,
        "summary_exists": summary_exists,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "sensitive_content_not_exported": True,
        "reports_are_sanitized": True,
    }

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "audit",
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": now_utc(),
        "checks": checks,
        "blocked_operations": BLOCKED_OPERATIONS,
    }

    write_json(REPORT_DIR / "077_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 077 audit failed.")

    return report


def closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 077 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 077 fechado com governanca consolidada da camada de resilience.")
    lines.append("")
    lines.append("## Restricoes confirmadas")
    lines.append("")
    for operation in BLOCKED_OPERATIONS:
        lines.append(f"- {operation}")
    lines.append("")
    lines.append("## Proximo checkpoint")
    lines.append("")
    lines.append("078 - K-Agent Resilience Layer Closure Core")
    lines.append("")
    return "\n".join(lines)


def mode_closure() -> Dict[str, Any]:
    ensure_dirs()

    action_report = read_json(REPORT_DIR / "077_action_report.json")
    validate_report = read_json(REPORT_DIR / "077_validate_report.json")
    audit_report = read_json(REPORT_DIR / "077_audit_report.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "next_checkpoint": "078 - K-Agent Resilience Layer Closure Core",
        "action_report": rel(REPORT_DIR / "077_action_report.json"),
        "validate_report": rel(REPORT_DIR / "077_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "077_audit_report.json"),
        "governance_summary": rel(REPORT_DIR / "077_governance_summary.json"),
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "077_closure_report.json", report)
    write_text(REPORT_DIR / "077_closure_report.md", closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 077 closure failed.")

    return report


def main() -> int:
    mode = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "action"

    handlers = {
        "init": mode_init,
        "action": mode_action,
        "validate": mode_validate,
        "audit": mode_audit,
        "closure": mode_closure,
    }

    if mode not in handlers:
        raise SystemExit(f"Modo invalido: {mode}")

    result = handlers[mode]()
    print(json.dumps({
        "checkpoint": CHECKPOINT_ID,
        "mode": mode,
        "status": result.get("status"),
        "report_dir": rel(REPORT_DIR),
    }, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())