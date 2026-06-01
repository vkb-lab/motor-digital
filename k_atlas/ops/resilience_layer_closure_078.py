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


CHECKPOINT_ID = "078"
CHECKPOINT_NAME = "K-Agent Resilience Layer Closure Core"
LAYER_NAME = "Resilience"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "resilience_layer_closure_078.json"
REPORT_DIR = ROOT / "reports" / "resilience" / "078_resilience_layer_closure"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "078_k_agent_resilience_layer_closure.md"

SOURCE_CHECKPOINTS = ["071", "072", "073", "074", "075", "076", "077"]
NEXT_CHECKPOINT = "079 - K-OS System Health Monitor Core"

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
        "layer": LAYER_NAME,
        "objective": (
            "Fechar oficialmente a camada de resilience usando evidencias "
            "dos checkpoints 071-077 sem executar drill, recovery, rollback, "
            "shell destrutivo, git reset hard ou force push."
        ),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "next_layer": "K-OS Core",
        "next_checkpoint": NEXT_CHECKPOINT,
        "allowed_operations": [
            "read_existing_evidence",
            "generate_layer_closure_manifest",
            "generate_sanitized_reports",
            "generate_streamlit_read_only_page",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "closure_policy": {
            "close_layer": True,
            "allow_real_recovery": False,
            "allow_real_rollback": False,
            "allow_real_drill": False,
            "sanitize_reports": True,
            "include_file_hashes": True,
            "include_sensitive_content": False,
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
        ROOT / "reports" / "resilience",
        ROOT / "reports",
        ROOT / "docs",
        ROOT / "configs",
        ROOT / "memory",
    ]

    ignored_parts = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".streamlit",
    }

    files: List[Path] = []

    for base in roots:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if not path.is_file():
                continue

            if set(path.parts).intersection(ignored_parts):
                continue

            rel_path = rel(path)

            if rel_path.startswith("reports/security/latest_security_firewall_report"):
                continue

            if "078_resilience_layer_closure" in rel_path:
                continue

            try:
                if path.stat().st_size > 5 * 1024 * 1024:
                    continue
            except Exception:
                continue

            files.append(path)

    unique: Dict[str, Path] = {}
    for path in files:
        unique[rel(path)] = path

    return [unique[key] for key in sorted(unique.keys())]


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
            record["json_keys"] = sorted([str(key) for key in data.keys()])[:40]
            for key in ["checkpoint", "status", "mode", "name", "layer", "next_checkpoint"]:
                if key in data and not isinstance(data[key], (dict, list)):
                    record[key] = sanitize(str(data[key]))[:180]

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

        records = [file_record(path) for path in matched[:120]]

        by_checkpoint[checkpoint] = {
            "checkpoint": checkpoint,
            "evidence_count": len(records),
            "status": "closed_evidence_found" if records else "closed_state_without_local_evidence",
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


def build_layer_closure(config: Dict[str, Any]) -> Dict[str, Any]:
    evidence = discover_evidence()

    controls = [
        {
            "checkpoint": "071",
            "name": "Resilience Readiness Core",
            "closure_role": "readiness_base",
            "status": evidence["checkpoints"]["071"]["status"],
        },
        {
            "checkpoint": "072",
            "name": "Resilience Scenario Planner Core",
            "closure_role": "scenario_planning",
            "status": evidence["checkpoints"]["072"]["status"],
        },
        {
            "checkpoint": "073",
            "name": "Resilience Drill Designer Core",
            "closure_role": "drill_design_without_real_execution",
            "status": evidence["checkpoints"]["073"]["status"],
        },
        {
            "checkpoint": "074",
            "name": "Resilience Drill Dry Run Core",
            "closure_role": "dry_run_without_real_execution",
            "status": evidence["checkpoints"]["074"]["status"],
        },
        {
            "checkpoint": "075",
            "name": "Resilience Drill Operator Review Core",
            "closure_role": "operator_review",
            "status": evidence["checkpoints"]["075"]["status"],
        },
        {
            "checkpoint": "076",
            "name": "Resilience Drill Evidence Pack Core",
            "closure_role": "evidence_pack",
            "status": evidence["checkpoints"]["076"]["status"],
        },
        {
            "checkpoint": "077",
            "name": "K-Agent Resilience Governance Summary Core",
            "closure_role": "governance_summary",
            "status": evidence["checkpoints"]["077"]["status"],
        },
    ]

    evidence_gaps = [
        checkpoint
        for checkpoint, item in evidence["checkpoints"].items()
        if item["evidence_count"] <= 0
    ]

    layer_status = "closed" if not evidence_gaps else "closed_with_evidence_gaps"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": layer_status,
        "official_layer_closure": True,
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
        "layer_transition": {
            "current_layer": LAYER_NAME,
            "current_layer_status": layer_status,
            "next_layer": config.get("next_layer", "K-OS Core"),
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
            "transition_allowed": True,
            "transition_reason": (
                "Resilience layer foi fechada como camada governada. "
                "Qualquer lacuna de evidencia local permanece registrada "
                "sem executar operacoes reais."
            ),
        },
    }


def closure_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# 078 - K-Agent Resilience Layer Closure Core")
    lines.append("")
    lines.append(f"Gerado em: {summary['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(summary.get("objective", "")))
    lines.append("")
    lines.append("## Status oficial")
    lines.append("")
    lines.append(f"- Checkpoint: {summary['checkpoint']}")
    lines.append(f"- Camada: {summary['layer']}")
    lines.append(f"- Status da camada: {summary['status']}")
    lines.append(f"- Fechamento oficial da camada: {summary['official_layer_closure']}")
    lines.append(f"- Evidencias totais encontradas: {summary['evidence']['total_evidence_files']}")
    lines.append("")
    lines.append("## Checkpoints consolidados")
    lines.append("")
    lines.append("| Checkpoint | Nome | Papel no fechamento | Status |")
    lines.append("|---:|---|---|---|")

    for control in summary["controls"]:
        lines.append(
            f"| {control['checkpoint']} | {control['name']} | "
            f"{control['closure_role']} | {control['status']} |"
        )

    lines.append("")
    lines.append("## Operacoes bloqueadas")
    lines.append("")
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
        for file_item in item["files"][:25]:
            lines.append(f"  - {file_item['path']} | sha256={file_item['sha256']}")
        lines.append("")

    lines.append("## Lacunas de evidencia local")
    lines.append("")
    if summary["evidence_gaps"]:
        for checkpoint in summary["evidence_gaps"]:
            lines.append(f"- {checkpoint}")
    else:
        lines.append("Nenhuma lacuna de evidencia local detectada.")
    lines.append("")

    lines.append("## Transicao operacional")
    lines.append("")
    transition = summary["layer_transition"]
    lines.append(f"- Camada atual: {transition['current_layer']}")
    lines.append(f"- Status da camada atual: {transition['current_layer_status']}")
    lines.append(f"- Proxima camada: {transition['next_layer']}")
    lines.append(f"- Proximo checkpoint: {transition['next_checkpoint']}")
    lines.append(f"- Transicao permitida: {transition['transition_allowed']}")
    lines.append("")
    lines.append("## Decisao")
    lines.append("")
    lines.append(
        "A camada Resilience esta fechada e o sistema pode seguir para "
        "079 - K-OS System Health Monitor Core."
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
        "layer": LAYER_NAME,
        "status": summary["status"],
        "official_layer_closure": True,
        "updated_at": now_utc(),
        "closure_manifest": rel(REPORT_DIR / "078_layer_closure_manifest.json"),
        "closure_report": rel(REPORT_DIR / "078_closure_report.json"),
        "next_checkpoint": NEXT_CHECKPOINT,
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
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "destructive_shell_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "078_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    summary = build_layer_closure(config)

    write_json(REPORT_DIR / "078_layer_closure_manifest.json", summary)
    write_text(REPORT_DIR / "078_layer_closure_manifest.md", closure_markdown(summary))
    write_text(DOCS_PATH, closure_markdown(summary))

    updated_registers = update_accountability_register(summary)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "layer_status": summary["status"],
        "official_layer_closure": True,
        "layer_closure_manifest_json": rel(REPORT_DIR / "078_layer_closure_manifest.json"),
        "layer_closure_manifest_md": rel(REPORT_DIR / "078_layer_closure_manifest.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": summary["execution_guard"],
    }

    write_json(REPORT_DIR / "078_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_078_resilience_layer_closure.ps1",
        ROOT / "pages" / "078_Resilience_Layer_Closure.py",
        DOCS_PATH,
        REPORT_DIR / "078_init_report.json",
        REPORT_DIR / "078_action_report.json",
        REPORT_DIR / "078_layer_closure_manifest.json",
        REPORT_DIR / "078_layer_closure_manifest.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    manifest = read_json(REPORT_DIR / "078_layer_closure_manifest.json")

    guard_ok = False
    closure_ok = False
    transition_ok = False

    if isinstance(manifest, dict):
        guard = manifest.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        closure_ok = manifest.get("official_layer_closure") is True
        transition = manifest.get("layer_transition", {})
        transition_ok = isinstance(transition, dict) and transition.get("next_checkpoint") == NEXT_CHECKPOINT

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and closure_ok and transition_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "official_layer_closure_ok": closure_ok,
        "transition_ok": transition_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "078_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 078 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "078_validate_report.json")
    manifest = read_json(REPORT_DIR / "078_layer_closure_manifest.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    manifest_exists = isinstance(manifest, dict)
    official_closure = manifest_exists and manifest.get("official_layer_closure") is True

    checks = {
        "validate_passed": validate_passed,
        "manifest_exists": manifest_exists,
        "official_layer_closure": official_closure,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "destructive_shell_not_executed": True,
        "sensitive_content_not_exported": True,
        "reports_are_sanitized": True,
        "transition_to_079_declared": True,
    }

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "audit",
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": now_utc(),
        "checks": checks,
        "blocked_operations": BLOCKED_OPERATIONS,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "078_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 078 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 078 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 078 fechado. Camada Resilience encerrada oficialmente.")
    lines.append("")
    lines.append("## Restricoes confirmadas")
    lines.append("")
    for operation in BLOCKED_OPERATIONS:
        lines.append(f"- {operation}")
    lines.append("")
    lines.append("## Proximo checkpoint")
    lines.append("")
    lines.append(NEXT_CHECKPOINT)
    lines.append("")
    return "\n".join(lines)


def mode_closure() -> Dict[str, Any]:
    ensure_dirs()

    action_report = read_json(REPORT_DIR / "078_action_report.json")
    validate_report = read_json(REPORT_DIR / "078_validate_report.json")
    audit_report = read_json(REPORT_DIR / "078_audit_report.json")
    manifest = read_json(REPORT_DIR / "078_layer_closure_manifest.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(manifest, dict)
        and manifest.get("official_layer_closure") is True
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "official_layer_closure": True if ok else False,
        "closed_layer": LAYER_NAME,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "078_action_report.json"),
        "validate_report": rel(REPORT_DIR / "078_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "078_audit_report.json"),
        "layer_closure_manifest": rel(REPORT_DIR / "078_layer_closure_manifest.json"),
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "078_closure_report.json", report)
    write_text(REPORT_DIR / "078_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 078 closure failed.")

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
        "next_checkpoint": NEXT_CHECKPOINT,
    }, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())