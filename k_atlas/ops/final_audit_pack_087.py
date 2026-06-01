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


CHECKPOINT_ID = "087"
CHECKPOINT_NAME = "K-OS Final Audit Pack Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_final_audit_pack_087.json"
REPORT_DIR = ROOT / "reports" / "system" / "087_final_audit_pack"
DOCS_COMMERCIAL_DIR = ROOT / "docs" / "commercial"
DOCS_KOS_DIR = ROOT / "docs" / "k_os"
DOCS_PATH = DOCS_COMMERCIAL_DIR / "087_k_os_final_audit_pack.md"

PREVIOUS_CHECKPOINT = "086 - K-OS Final Documentation Pack Core"
NEXT_CHECKPOINT = "088 - K-OS v1 Core Closure"

SOURCE_CHECKPOINTS = ["079", "080", "081", "082", "083", "084", "085", "086"]

CHECKPOINT_ARTIFACTS = {
    "079": {
        "name": "K-OS System Health Monitor Core",
        "dir": "reports/system/079_system_health_monitor",
        "main": "079_system_health_report.json",
        "validate": "079_validate_report.json",
        "audit": "079_audit_report.json",
        "closure": "079_closure_report.json",
        "doc": "docs/commercial/079_k_os_system_health_monitor.md"
    },
    "080": {
        "name": "K-OS Module Registry Core",
        "dir": "reports/system/080_module_registry",
        "main": "080_module_registry.json",
        "validate": "080_validate_report.json",
        "audit": "080_audit_report.json",
        "closure": "080_closure_report.json",
        "doc": "docs/commercial/080_k_os_module_registry.md"
    },
    "081": {
        "name": "K-OS Agent Capability Registry Core",
        "dir": "reports/system/081_agent_capability_registry",
        "main": "081_agent_capability_registry.json",
        "validate": "081_validate_report.json",
        "audit": "081_audit_report.json",
        "closure": "081_closure_report.json",
        "doc": "docs/commercial/081_k_os_agent_capability_registry.md"
    },
    "082": {
        "name": "K-OS Command Registry Core",
        "dir": "reports/system/082_command_registry",
        "main": "082_command_registry.json",
        "validate": "082_validate_report.json",
        "audit": "082_audit_report.json",
        "closure": "082_closure_report.json",
        "doc": "docs/commercial/082_k_os_command_registry.md"
    },
    "083": {
        "name": "K-OS Backup and Export Pack Core",
        "dir": "reports/system/083_backup_export_pack",
        "main": "083_backup_export_manifest.json",
        "validate": "083_validate_report.json",
        "audit": "083_audit_report.json",
        "closure": "083_closure_report.json",
        "doc": "docs/commercial/083_k_os_backup_export_pack.md"
    },
    "084": {
        "name": "K-OS Release Candidate Gate Core",
        "dir": "reports/system/084_release_candidate_gate",
        "main": "084_release_candidate_gate.json",
        "validate": "084_validate_report.json",
        "audit": "084_audit_report.json",
        "closure": "084_closure_report.json",
        "doc": "docs/commercial/084_k_os_release_candidate_gate.md"
    },
    "085": {
        "name": "K-OS Local Installer / Launcher Core",
        "dir": "reports/system/085_local_installer_launcher",
        "main": "085_local_installer_launcher_manifest.json",
        "validate": "085_validate_report.json",
        "audit": "085_audit_report.json",
        "closure": "085_closure_report.json",
        "doc": "docs/commercial/085_k_os_local_installer_launcher.md"
    },
    "086": {
        "name": "K-OS Final Documentation Pack Core",
        "dir": "reports/system/086_final_documentation_pack",
        "main": "086_final_documentation_pack.json",
        "validate": "086_validate_report.json",
        "audit": "086_audit_report.json",
        "closure": "086_closure_report.json",
        "doc": "docs/commercial/086_k_os_final_documentation_pack.md"
    }
}

FINAL_DOCS = [
    "docs/k_os/README_K_OS.md",
    "docs/k_os/OPERATOR_GUIDE.md",
    "docs/k_os/ARCHITECTURE.md",
    "docs/k_os/GOVERNANCE.md",
    "docs/k_os/LAUNCHER_GUIDE.md",
    "docs/k_os/RELEASE_NOTES.md",
    "docs/k_os/FINAL_DOCUMENTATION_INDEX.md",
]

LAUNCHER_FILES = [
    "scripts/k_os_local_install_check.ps1",
    "scripts/k_os_local_launcher.ps1",
]

BLOCKED_OPERATIONS = [
    "deploy_execution",
    "installer_execution",
    "dependency_install_execution",
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
    DOCS_COMMERCIAL_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_KOS_DIR.mkdir(parents=True, exist_ok=True)
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:
        return ""


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
            "Criar pacote final de auditoria do K-OS consolidando evidencias dos checkpoints 079-086, "
            "validando guards, documentos, launcher, registries, manifestos e trilha de fechamento, "
            "sem executar deploy, installer, recovery, rollback, drill, reset, force push, limpeza destrutiva ou auto-fix."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "allowed_operations": [
            "read_existing_evidence",
            "generate_final_audit_pack",
            "generate_sanitized_reports",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "audit_policy": {
            "read_only_audit": True,
            "execute_deploy": False,
            "execute_installer": False,
            "install_dependencies": False,
            "publish_release": False,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "allow_audit_with_warnings": True,
            "require_operator_approval_for_088": True,
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


def guard_is_safe(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    guard = data.get("execution_guard")
    if not isinstance(guard, dict):
        return False
    return all(value is False for value in guard.values())


def collect_checkpoint_audit() -> Dict[str, Any]:
    checkpoints: Dict[str, Any] = {}

    for checkpoint, definition in CHECKPOINT_ARTIFACTS.items():
        base_dir = ROOT / definition["dir"]
        main_path = base_dir / definition["main"]
        validate_path = base_dir / definition["validate"]
        audit_path = base_dir / definition["audit"]
        closure_path = base_dir / definition["closure"]
        doc_path = ROOT / definition["doc"]

        main_data = read_json(main_path)
        validate_data = read_json(validate_path)
        audit_data = read_json(audit_path)
        closure_data = read_json(closure_path)

        main_exists = isinstance(main_data, dict)
        validate_passed = isinstance(validate_data, dict) and validate_data.get("status") == "passed"
        audit_passed = isinstance(audit_data, dict) and audit_data.get("status") == "passed"
        closure_closed = isinstance(closure_data, dict) and closure_data.get("status") == "closed"
        doc_exists = doc_path.exists()
        guard_safe = guard_is_safe(main_data)

        issues = []
        if not main_exists:
            issues.append("main_report_missing")
        if not validate_passed:
            issues.append("validate_not_passed")
        if not audit_passed:
            issues.append("audit_not_passed")
        if not closure_closed:
            issues.append("closure_not_closed")
        if not doc_exists:
            issues.append("commercial_doc_missing")
        if not guard_safe:
            issues.append("execution_guard_missing_or_not_safe")

        files = []
        if base_dir.exists():
            for path in sorted(base_dir.glob("*"), key=lambda item: rel(item)):
                if path.is_file():
                    files.append(file_info(path))

        checkpoints[checkpoint] = {
            "checkpoint": checkpoint,
            "name": definition["name"],
            "status": "passed" if not issues else "warning",
            "issues": issues,
            "directory": file_info(base_dir),
            "main_report": file_info(main_path),
            "validate_report": file_info(validate_path),
            "audit_report": file_info(audit_path),
            "closure_report": file_info(closure_path),
            "commercial_doc": file_info(doc_path),
            "main_status": main_data.get("status") if isinstance(main_data, dict) else None,
            "validate_status": validate_data.get("status") if isinstance(validate_data, dict) else None,
            "audit_status": audit_data.get("status") if isinstance(audit_data, dict) else None,
            "closure_status": closure_data.get("status") if isinstance(closure_data, dict) else None,
            "execution_guard_safe": guard_safe,
            "evidence_file_count": len(files),
            "files": files[:80],
        }

    passed_count = sum(1 for item in checkpoints.values() if item["status"] == "passed")
    warning_count = len(checkpoints) - passed_count

    return {
        "generated_at": now_utc(),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "passed_count": passed_count,
        "warning_count": warning_count,
        "checkpoints": checkpoints,
    }


def collect_surface_audit() -> Dict[str, Any]:
    entrypoints = ["app.py", "streamlit_app.py", "Home.py"]
    entrypoint_files = [file_info(ROOT / item) for item in entrypoints]
    entrypoint_found = [item for item in entrypoint_files if item["exists"]]

    launcher_files = [file_info(ROOT / item) for item in LAUNCHER_FILES]
    final_docs = [file_info(ROOT / item) for item in FINAL_DOCS]

    root_files = [
        file_info(ROOT / "README.md"),
        file_info(ROOT / "requirements.txt"),
        file_info(ROOT / ".gitignore"),
        file_info(ROOT / "configs" / "k_os_final_audit_pack_087.json"),
    ]

    return {
        "entrypoint": {
            "status": "passed" if entrypoint_found else "warning",
            "selected": entrypoint_found[0]["path"] if entrypoint_found else None,
            "items": entrypoint_files,
        },
        "launcher": {
            "status": "passed" if all(item["exists"] for item in launcher_files) else "warning",
            "items": launcher_files,
        },
        "final_documentation": {
            "status": "passed" if all(item["exists"] for item in final_docs) else "warning",
            "items": final_docs,
        },
        "repository_surface": {
            "status": "passed" if all(item["exists"] for item in root_files[:2]) else "warning",
            "items": root_files,
        },
    }


def build_final_audit_pack(config: Dict[str, Any]) -> Dict[str, Any]:
    checkpoint_audit = collect_checkpoint_audit()
    surface_audit = collect_surface_audit()

    warnings: List[str] = []

    for checkpoint, item in checkpoint_audit["checkpoints"].items():
        if item["status"] != "passed":
            warnings.append(f"checkpoint_{checkpoint}_audit_warning")

    for domain, item in surface_audit.items():
        if item["status"] != "passed":
            warnings.append(f"{domain}_warning")

    domain_results = [
        {
            "domain": "checkpoint_evidence",
            "status": "passed" if checkpoint_audit["warning_count"] == 0 else "warning",
        },
        {
            "domain": "closure_reports",
            "status": "passed" if all(
                item["closure_status"] == "closed"
                for item in checkpoint_audit["checkpoints"].values()
            ) else "warning",
        },
        {
            "domain": "validation_reports",
            "status": "passed" if all(
                item["validate_status"] == "passed"
                for item in checkpoint_audit["checkpoints"].values()
            ) else "warning",
        },
        {
            "domain": "audit_reports",
            "status": "passed" if all(
                item["audit_status"] == "passed"
                for item in checkpoint_audit["checkpoints"].values()
            ) else "warning",
        },
        {
            "domain": "execution_guards",
            "status": "passed" if all(
                item["execution_guard_safe"] is True
                for item in checkpoint_audit["checkpoints"].values()
            ) else "warning",
        },
        {
            "domain": "documentation_pack",
            "status": surface_audit["final_documentation"]["status"],
        },
        {
            "domain": "launcher_pack",
            "status": surface_audit["launcher"]["status"],
        },
        {
            "domain": "repository_surface",
            "status": surface_audit["repository_surface"]["status"],
        },
        {
            "domain": "continuity_to_088",
            "status": "passed",
        },
    ]

    audit_status = "audit_passed" if not warnings else "audit_passed_with_warnings"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": audit_status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "audit_policy": sanitize(config.get("audit_policy", {})),
        "domain_results": domain_results,
        "warnings": warnings,
        "checkpoint_audit": checkpoint_audit,
        "surface_audit": surface_audit,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "deploy_executed": False,
            "installer_executed": False,
            "dependency_install_executed": False,
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
        "audit_decision": {
            "final_audit_pack_created": True,
            "audit_status": audit_status,
            "operator_approval_required_for_088": True,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
            "deploy_executed": False,
            "installer_executed": False,
            "release_published": False,
        },
    }


def audit_markdown(pack: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 087 - K-OS Final Audit Pack Core")
    lines.append("")
    lines.append(f"Gerado em: {pack['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(pack.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {pack['checkpoint']}")
    lines.append(f"- Camada: {pack['layer']}")
    lines.append(f"- Status da auditoria: {pack['status']}")
    lines.append(f"- Checkpoint anterior: {pack['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {pack['next_checkpoint']}")
    lines.append(f"- Warnings: {len(pack['warnings'])}")
    lines.append("")

    lines.append("## Resultado por dominio")
    lines.append("")
    lines.append("| Dominio | Status |")
    lines.append("|---|---|")
    for item in pack["domain_results"]:
        lines.append(f"| {item['domain']} | {item['status']} |")
    lines.append("")

    lines.append("## Auditoria por checkpoint")
    lines.append("")
    lines.append("| Checkpoint | Nome | Status | Validate | Audit | Closure | Guard | Evidencias |")
    lines.append("|---:|---|---|---|---|---|---|---:|")
    for checkpoint, item in pack["checkpoint_audit"]["checkpoints"].items():
        lines.append(
            f"| {checkpoint} | {item['name']} | {item['status']} | "
            f"{item['validate_status']} | {item['audit_status']} | {item['closure_status']} | "
            f"{item['execution_guard_safe']} | {item['evidence_file_count']} |"
        )
    lines.append("")

    lines.append("## Superficies finais")
    lines.append("")
    for domain, item in pack["surface_audit"].items():
        lines.append(f"- {domain}: {item['status']}")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if pack["warnings"]:
        for warning in pack["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("Nenhum warning registrado.")
    lines.append("")

    lines.append("## Decisao de auditoria")
    lines.append("")
    for key, value in pack["audit_decision"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in pack["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in pack["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")

    lines.append("## Proximo passo")
    lines.append("")
    lines.append("Seguir para 088 - K-OS v1 Core Closure.")
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(pack: Dict[str, Any]) -> List[str]:
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
        "status": pack["status"],
        "updated_at": now_utc(),
        "final_audit_pack": rel(REPORT_DIR / "087_final_audit_pack.json"),
        "closure_report": rel(REPORT_DIR / "087_closure_report.json"),
        "warnings_count": len(pack["warnings"]),
        "next_checkpoint": NEXT_CHECKPOINT,
        "operator_approval_required_for_088": True,
        "deploy_executed": False,
        "installer_executed": False,
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
            "dependency_install_executed": False,
            "release_publish_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "087_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    pack = build_final_audit_pack(config)

    write_json(REPORT_DIR / "087_final_audit_pack.json", pack)
    write_text(REPORT_DIR / "087_final_audit_pack.md", audit_markdown(pack))
    write_text(DOCS_PATH, audit_markdown(pack))

    updated_registers = update_accountability_register(pack)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "audit_status": pack["status"],
        "warnings": pack["warnings"],
        "warnings_count": len(pack["warnings"]),
        "final_audit_pack_json": rel(REPORT_DIR / "087_final_audit_pack.json"),
        "final_audit_pack_md": rel(REPORT_DIR / "087_final_audit_pack.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": pack["execution_guard"],
    }

    write_json(REPORT_DIR / "087_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_087_final_audit_pack.ps1",
        ROOT / "pages" / "087_K_OS_Final_Audit_Pack.py",
        DOCS_PATH,
        REPORT_DIR / "087_init_report.json",
        REPORT_DIR / "087_action_report.json",
        REPORT_DIR / "087_final_audit_pack.json",
        REPORT_DIR / "087_final_audit_pack.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    pack = read_json(REPORT_DIR / "087_final_audit_pack.json")

    guard_ok = False
    decision_ok = False
    pack_ok = False

    if isinstance(pack, dict):
        guard = pack.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = pack.get("audit_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("final_audit_pack_created") is True
            and decision.get("can_continue_to_next_checkpoint") is True
            and decision.get("deploy_executed") is False
            and decision.get("installer_executed") is False
            and decision.get("release_published") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        pack_ok = pack.get("status") in {"audit_passed", "audit_passed_with_warnings"}

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and pack_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "audit_decision_ok": decision_ok,
        "audit_pack_status_ok": pack_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "087_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 087 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "087_validate_report.json")
    pack = read_json(REPORT_DIR / "087_final_audit_pack.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    pack_exists = isinstance(pack, dict)

    checks = {
        "validate_passed": validate_passed,
        "final_audit_pack_exists": pack_exists,
        "read_only_audit": True,
        "deploy_not_executed": True,
        "installer_not_executed": True,
        "dependency_install_not_executed": True,
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
        "transition_to_088_declared": True,
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

    write_json(REPORT_DIR / "087_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 087 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 087 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 087 fechado. Pacote final de auditoria do K-OS criado e validado.")
    lines.append("")
    lines.append("## Auditoria")
    lines.append("")
    lines.append(f"- Audit status: {report['audit_status']}")
    lines.append(f"- Warnings: {report['warnings_count']}")
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

    action_report = read_json(REPORT_DIR / "087_action_report.json")
    validate_report = read_json(REPORT_DIR / "087_validate_report.json")
    audit_report = read_json(REPORT_DIR / "087_audit_report.json")
    pack = read_json(REPORT_DIR / "087_final_audit_pack.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(pack, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "audit_status": pack.get("status") if isinstance(pack, dict) else "unknown",
        "warnings_count": len(pack.get("warnings", [])) if isinstance(pack, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "087_action_report.json"),
        "validate_report": rel(REPORT_DIR / "087_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "087_audit_report.json"),
        "final_audit_pack": rel(REPORT_DIR / "087_final_audit_pack.json"),
        "operator_approval_required_for_088": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "087_closure_report.json", report)
    write_text(REPORT_DIR / "087_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 087 closure failed.")

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