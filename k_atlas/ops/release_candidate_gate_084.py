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


CHECKPOINT_ID = "084"
CHECKPOINT_NAME = "K-OS Release Candidate Gate Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_release_candidate_gate_084.json"
REPORT_DIR = ROOT / "reports" / "system" / "084_release_candidate_gate"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "084_k_os_release_candidate_gate.md"

PREVIOUS_CHECKPOINT = "083 - K-OS Backup and Export Pack Core"
NEXT_CHECKPOINT = "085 - K-OS Local Installer / Launcher Core"

SOURCE_CHECKPOINTS = ["079", "080", "081", "082", "083"]

CHECKPOINT_ARTIFACTS = {
    "079": {
        "name": "K-OS System Health Monitor Core",
        "dir": "reports/system/079_system_health_monitor",
        "main": "079_system_health_report.json",
        "closure": "079_closure_report.json",
        "validate": "079_validate_report.json",
        "audit": "079_audit_report.json"
    },
    "080": {
        "name": "K-OS Module Registry Core",
        "dir": "reports/system/080_module_registry",
        "main": "080_module_registry.json",
        "closure": "080_closure_report.json",
        "validate": "080_validate_report.json",
        "audit": "080_audit_report.json"
    },
    "081": {
        "name": "K-OS Agent Capability Registry Core",
        "dir": "reports/system/081_agent_capability_registry",
        "main": "081_agent_capability_registry.json",
        "closure": "081_closure_report.json",
        "validate": "081_validate_report.json",
        "audit": "081_audit_report.json"
    },
    "082": {
        "name": "K-OS Command Registry Core",
        "dir": "reports/system/082_command_registry",
        "main": "082_command_registry.json",
        "closure": "082_closure_report.json",
        "validate": "082_validate_report.json",
        "audit": "082_audit_report.json"
    },
    "083": {
        "name": "K-OS Backup and Export Pack Core",
        "dir": "reports/system/083_backup_export_pack",
        "main": "083_backup_export_manifest.json",
        "closure": "083_closure_report.json",
        "validate": "083_validate_report.json",
        "audit": "083_audit_report.json"
    }
}

BLOCKED_OPERATIONS = [
    "deploy_execution",
    "installer_execution",
    "release_publish_execution",
    "backup_restore_execution",
    "real_drill_execution",
    "real_recovery_execution",
    "real_rollback_execution",
    "git_reset_hard",
    "force_push",
    "destructive_shell",
    "memory_deletion",
    "secret_export",
    "automatic_remediation",
]

SENSITIVE_KEY_RE = re.compile(
    r"(secret|token|password|credential|authorization|private_key|api_key|bearer)",
    re.IGNORECASE,
)

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"sk-[0-9A-Za-z_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
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


def file_info(path: Path) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "path": rel(path),
        "exists": path.exists(),
    }

    if path.exists() and path.is_file():
        stat = path.stat()
        item.update({
            "type": "file",
            "size_bytes": stat.st_size,
            "modified_utc": dt.datetime.fromtimestamp(
                stat.st_mtime,
                tz=dt.timezone.utc,
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "sha256": sha256_file(path),
        })

        if path.suffix.lower() == ".json":
            data = read_json(path)
            if isinstance(data, dict):
                item["status"] = data.get("status")
                item["checkpoint"] = data.get("checkpoint")
                item["mode"] = data.get("mode")
                item["next_checkpoint"] = data.get("next_checkpoint")

    elif path.exists() and path.is_dir():
        item.update({
            "type": "directory",
            "file_count": sum(1 for child in path.rglob("*") if child.is_file()),
        })
    else:
        item["type"] = "missing"

    return item


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar gate de Release Candidate do K-OS consolidando evidencias "
            "dos checkpoints 079-083, avaliando prontidao operacional, riscos, "
            "bloqueios e transicao para installer local, sem executar deploy, "
            "recovery, rollback, drill, reset, force push, limpeza destrutiva ou auto-fix."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "gate_domains": [
            "system_health",
            "module_registry",
            "agent_capability_registry",
            "command_registry",
            "backup_export_pack",
            "security_policy",
            "governance_guards",
            "streamlit_surface",
            "documentation_surface",
        ],
        "allowed_operations": [
            "read_existing_evidence",
            "generate_release_candidate_gate",
            "generate_sanitized_reports",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "gate_policy": {
            "read_only_gate": True,
            "execute_deploy": False,
            "execute_installer": False,
            "publish_release": False,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "allow_rc_with_warnings": True,
            "require_operator_approval_for_next_checkpoint": True,
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


def evidence_summary_for_checkpoint(checkpoint: str, definition: Dict[str, str]) -> Dict[str, Any]:
    base_dir = ROOT / definition["dir"]

    main_path = base_dir / definition["main"]
    closure_path = base_dir / definition["closure"]
    validate_path = base_dir / definition["validate"]
    audit_path = base_dir / definition["audit"]

    main_data = read_json(main_path)
    closure_data = read_json(closure_path)
    validate_data = read_json(validate_path)
    audit_data = read_json(audit_path)

    files = []
    if base_dir.exists():
        for path in sorted(base_dir.glob("*"), key=lambda item: rel(item)):
            if path.is_file():
                files.append(file_info(path))

    validate_passed = isinstance(validate_data, dict) and validate_data.get("status") == "passed"
    audit_passed = isinstance(audit_data, dict) and audit_data.get("status") == "passed"
    closure_closed = isinstance(closure_data, dict) and closure_data.get("status") == "closed"
    main_exists = isinstance(main_data, dict)

    evidence_status = (
        "ready"
        if main_exists and closure_closed and validate_passed and audit_passed
        else "warning"
    )

    return {
        "checkpoint": checkpoint,
        "name": definition["name"],
        "directory": rel(base_dir),
        "directory_exists": base_dir.exists(),
        "main_report": file_info(main_path),
        "closure_report": file_info(closure_path),
        "validate_report": file_info(validate_path),
        "audit_report": file_info(audit_path),
        "main_status": main_data.get("status") if isinstance(main_data, dict) else None,
        "closure_status": closure_data.get("status") if isinstance(closure_data, dict) else None,
        "validate_status": validate_data.get("status") if isinstance(validate_data, dict) else None,
        "audit_status": audit_data.get("status") if isinstance(audit_data, dict) else None,
        "validate_passed": validate_passed,
        "audit_passed": audit_passed,
        "closure_closed": closure_closed,
        "main_exists": main_exists,
        "evidence_file_count": len(files),
        "files": files[:80],
        "evidence_status": evidence_status,
    }


def collect_gate_evidence() -> Dict[str, Any]:
    checkpoints = {}

    for checkpoint in SOURCE_CHECKPOINTS:
        checkpoints[checkpoint] = evidence_summary_for_checkpoint(
            checkpoint,
            CHECKPOINT_ARTIFACTS[checkpoint],
        )

    ready_count = sum(1 for item in checkpoints.values() if item["evidence_status"] == "ready")
    warning_count = len(checkpoints) - ready_count

    return {
        "generated_at": now_utc(),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "ready_count": ready_count,
        "warning_count": warning_count,
        "checkpoints": checkpoints,
    }


def collect_surface_checks() -> Dict[str, Any]:
    streamlit_candidates = ["app.py", "streamlit_app.py", "Home.py"]
    docs_candidates = [
        "README.md",
        "docs/commercial/079_k_os_system_health_monitor.md",
        "docs/commercial/080_k_os_module_registry.md",
        "docs/commercial/081_k_os_agent_capability_registry.md",
        "docs/commercial/082_k_os_command_registry.md",
        "docs/commercial/083_k_os_backup_export_pack.md",
    ]

    streamlit_found = [file_info(ROOT / item) for item in streamlit_candidates if (ROOT / item).exists()]
    docs_status = [file_info(ROOT / item) for item in docs_candidates]

    return {
        "streamlit_surface": {
            "status": "ready" if streamlit_found else "warning",
            "candidates": streamlit_candidates,
            "found": streamlit_found,
            "selected": streamlit_found[0]["path"] if streamlit_found else None,
        },
        "documentation_surface": {
            "status": "ready" if all(item["exists"] for item in docs_status[:1]) else "warning",
            "documents": docs_status,
        },
    }


def build_release_candidate_gate(config: Dict[str, Any]) -> Dict[str, Any]:
    evidence = collect_gate_evidence()
    surfaces = collect_surface_checks()

    warnings: List[str] = []

    for checkpoint, item in evidence["checkpoints"].items():
        if item["evidence_status"] != "ready":
            warnings.append(f"checkpoint_{checkpoint}_evidence_warning")

    if surfaces["streamlit_surface"]["status"] != "ready":
        warnings.append("streamlit_surface_warning")

    if surfaces["documentation_surface"]["status"] != "ready":
        warnings.append("documentation_surface_warning")

    gate_status = "rc_ready" if not warnings else "rc_ready_with_warnings"

    gate_decision = {
        "release_candidate_gate_created": True,
        "release_candidate_status": gate_status,
        "operator_approval_required": True,
        "can_continue_to_next_checkpoint": True,
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
    }

    domain_gates = [
        {
            "domain": "system_health",
            "source_checkpoint": "079",
            "status": evidence["checkpoints"]["079"]["evidence_status"],
        },
        {
            "domain": "module_registry",
            "source_checkpoint": "080",
            "status": evidence["checkpoints"]["080"]["evidence_status"],
        },
        {
            "domain": "agent_capability_registry",
            "source_checkpoint": "081",
            "status": evidence["checkpoints"]["081"]["evidence_status"],
        },
        {
            "domain": "command_registry",
            "source_checkpoint": "082",
            "status": evidence["checkpoints"]["082"]["evidence_status"],
        },
        {
            "domain": "backup_export_pack",
            "source_checkpoint": "083",
            "status": evidence["checkpoints"]["083"]["evidence_status"],
        },
        {
            "domain": "streamlit_surface",
            "source_checkpoint": "local_surface",
            "status": surfaces["streamlit_surface"]["status"],
        },
        {
            "domain": "documentation_surface",
            "source_checkpoint": "local_surface",
            "status": surfaces["documentation_surface"]["status"],
        },
        {
            "domain": "governance_guards",
            "source_checkpoint": "084",
            "status": "ready",
        },
        {
            "domain": "security_policy",
            "source_checkpoint": "084",
            "status": "ready",
        },
    ]

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": gate_status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "gate_policy": sanitize(config.get("gate_policy", {})),
        "domain_gates": domain_gates,
        "warnings": warnings,
        "evidence": evidence,
        "surfaces": surfaces,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "deploy_executed": False,
            "installer_executed": False,
            "release_publish_executed": False,
            "backup_restore_executed": False,
            "automatic_remediation_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "git_reset_hard_executed": False,
            "force_push_executed": False,
            "destructive_shell_executed": False,
            "memory_deletion_executed": False,
            "secret_export_executed": False,
        },
        "gate_decision": gate_decision,
    }


def gate_markdown(gate: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# 084 - K-OS Release Candidate Gate Core")
    lines.append("")
    lines.append(f"Gerado em: {gate['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(gate.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {gate['checkpoint']}")
    lines.append(f"- Camada: {gate['layer']}")
    lines.append(f"- Status do gate: {gate['status']}")
    lines.append(f"- Checkpoint anterior: {gate['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {gate['next_checkpoint']}")
    lines.append(f"- Operador deve aprovar proximo checkpoint: {gate['gate_decision']['operator_approval_required']}")
    lines.append("")

    lines.append("## Gate por dominio")
    lines.append("")
    lines.append("| Dominio | Fonte | Status |")
    lines.append("|---|---|---|")
    for item in gate["domain_gates"]:
        lines.append(f"| {item['domain']} | {item['source_checkpoint']} | {item['status']} |")
    lines.append("")

    lines.append("## Evidencias por checkpoint")
    lines.append("")
    lines.append("| Checkpoint | Nome | Main | Validate | Audit | Closure | Status |")
    lines.append("|---:|---|---|---|---|---|---|")
    for checkpoint, item in gate["evidence"]["checkpoints"].items():
        lines.append(
            f"| {checkpoint} | {item['name']} | {item['main_exists']} | "
            f"{item['validate_status']} | {item['audit_status']} | "
            f"{item['closure_status']} | {item['evidence_status']} |"
        )
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if gate["warnings"]:
        for warning in gate["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("Nenhum warning registrado.")
    lines.append("")

    lines.append("## Decisao do gate")
    lines.append("")
    for key, value in gate["gate_decision"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in gate["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in gate["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")

    lines.append("## Proximo passo")
    lines.append("")
    lines.append("Seguir para 085 - K-OS Local Installer / Launcher Core.")
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(gate: Dict[str, Any]) -> List[str]:
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
        "status": gate["status"],
        "updated_at": now_utc(),
        "release_candidate_gate": rel(REPORT_DIR / "084_release_candidate_gate.json"),
        "closure_report": rel(REPORT_DIR / "084_closure_report.json"),
        "next_checkpoint": NEXT_CHECKPOINT,
        "operator_approval_required": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
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
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "deploy_executed": False,
            "installer_executed": False,
            "release_publish_executed": False,
            "backup_restore_executed": False,
            "automatic_remediation_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "084_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    gate = build_release_candidate_gate(config)

    write_json(REPORT_DIR / "084_release_candidate_gate.json", gate)
    write_text(REPORT_DIR / "084_release_candidate_gate.md", gate_markdown(gate))
    write_text(DOCS_PATH, gate_markdown(gate))

    updated_registers = update_accountability_register(gate)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "gate_status": gate["status"],
        "warnings": gate["warnings"],
        "release_candidate_gate_json": rel(REPORT_DIR / "084_release_candidate_gate.json"),
        "release_candidate_gate_md": rel(REPORT_DIR / "084_release_candidate_gate.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "operator_approval_required": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": gate["execution_guard"],
    }

    write_json(REPORT_DIR / "084_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_084_release_candidate_gate.ps1",
        ROOT / "pages" / "084_K_OS_Release_Candidate_Gate.py",
        DOCS_PATH,
        REPORT_DIR / "084_init_report.json",
        REPORT_DIR / "084_action_report.json",
        REPORT_DIR / "084_release_candidate_gate.json",
        REPORT_DIR / "084_release_candidate_gate.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    gate = read_json(REPORT_DIR / "084_release_candidate_gate.json")

    guard_ok = False
    decision_ok = False
    gate_ok = False

    if isinstance(gate, dict):
        guard = gate.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = gate.get("gate_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("release_candidate_gate_created") is True
            and decision.get("can_continue_to_next_checkpoint") is True
            and decision.get("deploy_executed") is False
            and decision.get("installer_executed") is False
            and decision.get("release_published") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        gate_ok = gate.get("status") in {"rc_ready", "rc_ready_with_warnings"}

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and gate_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "gate_decision_ok": decision_ok,
        "gate_status_ok": gate_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "084_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 084 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "084_validate_report.json")
    gate = read_json(REPORT_DIR / "084_release_candidate_gate.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    gate_exists = isinstance(gate, dict)

    checks = {
        "validate_passed": validate_passed,
        "release_candidate_gate_exists": gate_exists,
        "read_only_gate": True,
        "deploy_not_executed": True,
        "installer_not_executed": True,
        "release_not_published": True,
        "backup_restore_not_executed": True,
        "automatic_remediation_not_executed": True,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "destructive_shell_not_executed": True,
        "memory_deletion_not_executed": True,
        "secret_export_not_executed": True,
        "reports_are_sanitized": True,
        "transition_to_085_declared": True,
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

    write_json(REPORT_DIR / "084_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 084 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 084 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 084 fechado. Gate de Release Candidate criado em modo somente leitura.")
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

    action_report = read_json(REPORT_DIR / "084_action_report.json")
    validate_report = read_json(REPORT_DIR / "084_validate_report.json")
    audit_report = read_json(REPORT_DIR / "084_audit_report.json")
    gate = read_json(REPORT_DIR / "084_release_candidate_gate.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(gate, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "gate_status": gate.get("status") if isinstance(gate, dict) else "unknown",
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "084_action_report.json"),
        "validate_report": rel(REPORT_DIR / "084_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "084_audit_report.json"),
        "release_candidate_gate": rel(REPORT_DIR / "084_release_candidate_gate.json"),
        "operator_approval_required": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "084_closure_report.json", report)
    write_text(REPORT_DIR / "084_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 084 closure failed.")

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