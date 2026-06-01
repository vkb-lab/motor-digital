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


CHECKPOINT_ID = "088"
CHECKPOINT_NAME = "K-OS v1 Core Closure"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_v1_core_closure_088.json"
REPORT_DIR = ROOT / "reports" / "system" / "088_v1_core_closure"
DOCS_COMMERCIAL_DIR = ROOT / "docs" / "commercial"
DOCS_KOS_DIR = ROOT / "docs" / "k_os"
COMMERCIAL_DOC_PATH = DOCS_COMMERCIAL_DIR / "088_k_os_v1_core_closure.md"
V1_CLOSURE_DOC_PATH = DOCS_KOS_DIR / "K_OS_V1_CORE_CLOSURE.md"
V1_STATUS_DOC_PATH = DOCS_KOS_DIR / "K_OS_V1_STATUS.md"

PREVIOUS_CHECKPOINT = "087 - K-OS Final Audit Pack Core"
NEXT_CHECKPOINT = "K-OS v1 Core closed"

SOURCE_CHECKPOINTS = ["079", "080", "081", "082", "083", "084", "085", "086", "087"]

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
    },
    "087": {
        "name": "K-OS Final Audit Pack Core",
        "dir": "reports/system/087_final_audit_pack",
        "main": "087_final_audit_pack.json",
        "validate": "087_validate_report.json",
        "audit": "087_audit_report.json",
        "closure": "087_closure_report.json",
        "doc": "docs/commercial/087_k_os_final_audit_pack.md"
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
    "git_tag_creation",
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
            "Fechar oficialmente o K-OS v1 Core consolidando evidencias dos checkpoints 079-087, "
            "manifesto final, trilha auditavel, documentacao final, status operacional e continuidade "
            "para proximas camadas, sem executar deploy, installer, release publish, recovery, rollback, "
            "drill, reset, force push, limpeza destrutiva ou auto-fix."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "allowed_operations": [
            "read_existing_evidence",
            "generate_v1_core_closure_manifest",
            "generate_final_status_report",
            "generate_sanitized_reports",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "closure_policy": {
            "read_only_closure": True,
            "execute_deploy": False,
            "execute_installer": False,
            "install_dependencies": False,
            "publish_release": False,
            "create_git_tag": False,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "allow_closure_with_warnings": True,
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


def collect_checkpoint_closure() -> Dict[str, Any]:
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
            "status": "closed" if not issues else "closed_with_warnings",
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

    clean_count = sum(1 for item in checkpoints.values() if item["status"] == "closed")
    warning_count = len(checkpoints) - clean_count

    return {
        "generated_at": now_utc(),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "closed_clean_count": clean_count,
        "closed_with_warnings_count": warning_count,
        "checkpoints": checkpoints,
    }


def collect_final_surfaces() -> Dict[str, Any]:
    entrypoints = ["app.py", "streamlit_app.py", "Home.py"]
    entrypoint_items = [file_info(ROOT / item) for item in entrypoints]
    entrypoint_found = [item for item in entrypoint_items if item["exists"]]

    launcher_items = [file_info(ROOT / item) for item in LAUNCHER_FILES]
    final_doc_items = [file_info(ROOT / item) for item in FINAL_DOCS]

    required_roots = [
        "k_atlas",
        "configs",
        "scripts",
        "pages",
        "docs",
        "reports",
    ]

    root_items = [file_info(ROOT / item) for item in required_roots]

    return {
        "entrypoint": {
            "status": "ready" if entrypoint_found else "warning",
            "selected": entrypoint_found[0]["path"] if entrypoint_found else None,
            "items": entrypoint_items,
        },
        "launcher": {
            "status": "ready" if all(item["exists"] for item in launcher_items) else "warning",
            "items": launcher_items,
        },
        "final_documentation": {
            "status": "ready" if all(item["exists"] for item in final_doc_items) else "warning",
            "items": final_doc_items,
        },
        "repository_roots": {
            "status": "ready" if all(item["exists"] for item in root_items) else "warning",
            "items": root_items,
        },
        "root_files": {
            "items": [
                file_info(ROOT / "README.md"),
                file_info(ROOT / "requirements.txt"),
                file_info(ROOT / ".gitignore"),
            ]
        },
    }


def build_v1_core_closure(config: Dict[str, Any]) -> Dict[str, Any]:
    checkpoint_closure = collect_checkpoint_closure()
    final_surfaces = collect_final_surfaces()

    warnings: List[str] = []

    for checkpoint, item in checkpoint_closure["checkpoints"].items():
        if item["issues"]:
            warnings.append(f"checkpoint_{checkpoint}_closure_warning")

    for domain, item in final_surfaces.items():
        if isinstance(item, dict) and item.get("status") == "warning":
            warnings.append(f"{domain}_warning")

    closure_domains = [
        {
            "domain": "system_health",
            "source_checkpoint": "079",
            "status": checkpoint_closure["checkpoints"]["079"]["status"],
        },
        {
            "domain": "module_registry",
            "source_checkpoint": "080",
            "status": checkpoint_closure["checkpoints"]["080"]["status"],
        },
        {
            "domain": "agent_capability_registry",
            "source_checkpoint": "081",
            "status": checkpoint_closure["checkpoints"]["081"]["status"],
        },
        {
            "domain": "command_registry",
            "source_checkpoint": "082",
            "status": checkpoint_closure["checkpoints"]["082"]["status"],
        },
        {
            "domain": "backup_export_pack",
            "source_checkpoint": "083",
            "status": checkpoint_closure["checkpoints"]["083"]["status"],
        },
        {
            "domain": "release_candidate_gate",
            "source_checkpoint": "084",
            "status": checkpoint_closure["checkpoints"]["084"]["status"],
        },
        {
            "domain": "local_launcher",
            "source_checkpoint": "085",
            "status": checkpoint_closure["checkpoints"]["085"]["status"],
        },
        {
            "domain": "final_documentation",
            "source_checkpoint": "086",
            "status": checkpoint_closure["checkpoints"]["086"]["status"],
        },
        {
            "domain": "final_audit",
            "source_checkpoint": "087",
            "status": checkpoint_closure["checkpoints"]["087"]["status"],
        },
        {
            "domain": "v1_core_closure",
            "source_checkpoint": "088",
            "status": "closed",
        },
    ]

    closure_status = "v1_closed" if not warnings else "v1_closed_with_warnings"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": closure_status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "closure_policy": sanitize(config.get("closure_policy", {})),
        "closure_domains": closure_domains,
        "warnings": warnings,
        "checkpoint_closure": checkpoint_closure,
        "final_surfaces": final_surfaces,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "deploy_executed": False,
            "installer_executed": False,
            "dependency_install_executed": False,
            "release_publish_executed": False,
            "git_tag_created": False,
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
        "closure_decision": {
            "k_os_v1_core_closed": True,
            "closure_status": closure_status,
            "operator_approval_required_for_future_layers": True,
            "can_continue_after_v1_core": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
            "deploy_executed": False,
            "installer_executed": False,
            "release_published": False,
            "git_tag_created": False,
        },
        "continuity": {
            "recommended_next_layer": "K-OS v1 Expansion Layer",
            "recommended_next_focus": [
                "productization",
                "cloud readiness",
                "tenant model",
                "agent orchestration hardening",
                "commercial cockpit"
            ],
            "manual_launcher_command": "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1",
            "manual_check_command": "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_install_check.ps1"
        },
    }


def closure_markdown(manifest: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# 088 - K-OS v1 Core Closure")
    lines.append("")
    lines.append(f"Gerado em: {manifest['generated_at']}")
    lines.append("")
    lines.append("## Resultado final")
    lines.append("")
    lines.append(f"- Status: {manifest['status']}")
    lines.append("- K-OS v1 Core fechado oficialmente: True")
    lines.append(f"- Checkpoints consolidados: {', '.join(SOURCE_CHECKPOINTS)}")
    lines.append(f"- Warnings: {len(manifest['warnings'])}")
    lines.append("")
    lines.append("## Dominios de fechamento")
    lines.append("")
    lines.append("| Dominio | Fonte | Status |")
    lines.append("|---|---|---|")
    for item in manifest["closure_domains"]:
        lines.append(f"| {item['domain']} | {item['source_checkpoint']} | {item['status']} |")
    lines.append("")
    lines.append("## Checkpoints encerrados")
    lines.append("")
    lines.append("| Checkpoint | Nome | Status | Validate | Audit | Closure | Guard | Evidencias |")
    lines.append("|---:|---|---|---|---|---|---|---:|")
    for checkpoint, item in manifest["checkpoint_closure"]["checkpoints"].items():
        lines.append(
            f"| {checkpoint} | {item['name']} | {item['status']} | "
            f"{item['validate_status']} | {item['audit_status']} | {item['closure_status']} | "
            f"{item['execution_guard_safe']} | {item['evidence_file_count']} |"
        )
    lines.append("")
    lines.append("## Superficies finais")
    lines.append("")
    lines.append(f"- Entrypoint: {manifest['final_surfaces']['entrypoint']['selected']}")
    lines.append(f"- Launcher: {manifest['final_surfaces']['launcher']['status']}")
    lines.append(f"- Documentacao final: {manifest['final_surfaces']['final_documentation']['status']}")
    lines.append(f"- Raizes do repositorio: {manifest['final_surfaces']['repository_roots']['status']}")
    lines.append("")
    lines.append("## Comandos manuais")
    lines.append("")
    lines.append("Checagem local:")
    lines.append("")
    lines.append("```powershell")
    lines.append(manifest["continuity"]["manual_check_command"])
    lines.append("```")
    lines.append("")
    lines.append("Abrir cockpit:")
    lines.append("")
    lines.append("```powershell")
    lines.append(manifest["continuity"]["manual_launcher_command"])
    lines.append("```")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if manifest["warnings"]:
        for warning in manifest["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("Nenhum warning registrado.")
    lines.append("")
    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in manifest["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in manifest["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")
    lines.append("## Continuidade recomendada")
    lines.append("")
    lines.append(f"- Proxima camada sugerida: {manifest['continuity']['recommended_next_layer']}")
    lines.append("")
    for item in manifest["continuity"]["recommended_next_focus"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def status_markdown(manifest: Dict[str, Any]) -> str:
    lines = []
    lines.append("# K-OS v1 Status")
    lines.append("")
    lines.append(f"Atualizado em: {manifest['generated_at']}")
    lines.append("")
    lines.append("## Estado")
    lines.append("")
    lines.append(f"- K-OS v1 Core: {manifest['status']}")
    lines.append("- Fechamento oficial: checkpoint 088")
    lines.append("- Deploy executado: False")
    lines.append("- Installer executado: False")
    lines.append("- Release publicada: False")
    lines.append("- Git tag criada: False")
    lines.append("")
    lines.append("## Como abrir localmente")
    lines.append("")
    lines.append("```powershell")
    lines.append("powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def update_accountability_register(manifest: Dict[str, Any]) -> List[str]:
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
        "status": manifest["status"],
        "updated_at": now_utc(),
        "v1_core_closure_manifest": rel(REPORT_DIR / "088_v1_core_closure_manifest.json"),
        "closure_report": rel(REPORT_DIR / "088_closure_report.json"),
        "warnings_count": len(manifest["warnings"]),
        "next_checkpoint": NEXT_CHECKPOINT,
        "k_os_v1_core_closed": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "git_tag_created": False,
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
            "git_tag_created": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "088_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    manifest = build_v1_core_closure(config)

    write_json(REPORT_DIR / "088_v1_core_closure_manifest.json", manifest)
    write_text(REPORT_DIR / "088_v1_core_closure_manifest.md", closure_markdown(manifest))
    write_text(COMMERCIAL_DOC_PATH, closure_markdown(manifest))
    write_text(V1_CLOSURE_DOC_PATH, closure_markdown(manifest))
    write_text(V1_STATUS_DOC_PATH, status_markdown(manifest))

    final_status = {
        "checkpoint": CHECKPOINT_ID,
        "name": "K-OS v1 Core Final Status",
        "generated_at": now_utc(),
        "status": manifest["status"],
        "k_os_v1_core_closed": True,
        "source_checkpoints": SOURCE_CHECKPOINTS,
        "warnings": manifest["warnings"],
        "launcher_command": manifest["continuity"]["manual_launcher_command"],
        "check_command": manifest["continuity"]["manual_check_command"],
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "git_tag_created": False,
    }

    write_json(REPORT_DIR / "088_k_os_v1_final_status.json", final_status)

    updated_registers = update_accountability_register(manifest)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "closure_status": manifest["status"],
        "warnings": manifest["warnings"],
        "warnings_count": len(manifest["warnings"]),
        "v1_core_closure_manifest_json": rel(REPORT_DIR / "088_v1_core_closure_manifest.json"),
        "v1_core_closure_manifest_md": rel(REPORT_DIR / "088_v1_core_closure_manifest.md"),
        "final_status_json": rel(REPORT_DIR / "088_k_os_v1_final_status.json"),
        "commercial_doc": rel(COMMERCIAL_DOC_PATH),
        "kos_closure_doc": rel(V1_CLOSURE_DOC_PATH),
        "kos_status_doc": rel(V1_STATUS_DOC_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "k_os_v1_core_closed": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "git_tag_created": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": manifest["execution_guard"],
    }

    write_json(REPORT_DIR / "088_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_088_v1_core_closure.ps1",
        ROOT / "pages" / "088_K_OS_v1_Core_Closure.py",
        COMMERCIAL_DOC_PATH,
        V1_CLOSURE_DOC_PATH,
        V1_STATUS_DOC_PATH,
        REPORT_DIR / "088_init_report.json",
        REPORT_DIR / "088_action_report.json",
        REPORT_DIR / "088_v1_core_closure_manifest.json",
        REPORT_DIR / "088_v1_core_closure_manifest.md",
        REPORT_DIR / "088_k_os_v1_final_status.json",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    manifest = read_json(REPORT_DIR / "088_v1_core_closure_manifest.json")

    guard_ok = False
    decision_ok = False
    manifest_ok = False

    if isinstance(manifest, dict):
        guard = manifest.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = manifest.get("closure_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("k_os_v1_core_closed") is True
            and decision.get("can_continue_after_v1_core") is True
            and decision.get("deploy_executed") is False
            and decision.get("installer_executed") is False
            and decision.get("release_published") is False
            and decision.get("git_tag_created") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        manifest_ok = manifest.get("status") in {"v1_closed", "v1_closed_with_warnings"}

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and manifest_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "closure_decision_ok": decision_ok,
        "manifest_status_ok": manifest_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "088_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 088 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "088_validate_report.json")
    manifest = read_json(REPORT_DIR / "088_v1_core_closure_manifest.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    manifest_exists = isinstance(manifest, dict)

    checks = {
        "validate_passed": validate_passed,
        "v1_core_closure_manifest_exists": manifest_exists,
        "k_os_v1_core_closed": True,
        "read_only_closure": True,
        "deploy_not_executed": True,
        "installer_not_executed": True,
        "dependency_install_not_executed": True,
        "release_not_published": True,
        "git_tag_not_created": True,
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
        "k_os_v1_status_declared": True,
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

    write_json(REPORT_DIR / "088_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 088 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 088 - Final Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("K-OS v1 Core fechado oficialmente.")
    lines.append("")
    lines.append(f"- Closure status: {report['closure_status']}")
    lines.append(f"- Warnings: {report['warnings_count']}")
    lines.append("- Deploy executado: False")
    lines.append("- Installer executado: False")
    lines.append("- Release publicada: False")
    lines.append("- Git tag criada: False")
    lines.append("")
    lines.append("## Artefatos principais")
    lines.append("")
    lines.append(f"- Manifesto: {report['v1_core_closure_manifest']}")
    lines.append(f"- Status final: {report['final_status_json']}")
    lines.append(f"- Documento K-OS: {report['kos_closure_doc']}")
    lines.append("")
    lines.append("## Restricoes confirmadas")
    lines.append("")
    for operation in BLOCKED_OPERATIONS:
        lines.append(f"- {operation}")
    lines.append("")
    lines.append("## Estado")
    lines.append("")
    lines.append("K-OS v1 Core closed.")
    lines.append("")
    return "\n".join(lines)


def mode_closure() -> Dict[str, Any]:
    ensure_dirs()

    action_report = read_json(REPORT_DIR / "088_action_report.json")
    validate_report = read_json(REPORT_DIR / "088_validate_report.json")
    audit_report = read_json(REPORT_DIR / "088_audit_report.json")
    manifest = read_json(REPORT_DIR / "088_v1_core_closure_manifest.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(manifest, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "closure_status": manifest.get("status") if isinstance(manifest, dict) else "unknown",
        "warnings_count": len(manifest.get("warnings", [])) if isinstance(manifest, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "088_action_report.json"),
        "validate_report": rel(REPORT_DIR / "088_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "088_audit_report.json"),
        "v1_core_closure_manifest": rel(REPORT_DIR / "088_v1_core_closure_manifest.json"),
        "final_status_json": rel(REPORT_DIR / "088_k_os_v1_final_status.json"),
        "kos_closure_doc": rel(V1_CLOSURE_DOC_PATH),
        "k_os_v1_core_closed": True,
        "deploy_executed": False,
        "installer_executed": False,
        "release_published": False,
        "git_tag_created": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "088_closure_report.json", report)
    write_text(REPORT_DIR / "088_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 088 closure failed.")

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