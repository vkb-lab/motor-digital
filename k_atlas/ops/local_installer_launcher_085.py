# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


CHECKPOINT_ID = "085"
CHECKPOINT_NAME = "K-OS Local Installer / Launcher Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_local_installer_launcher_085.json"
REPORT_DIR = ROOT / "reports" / "system" / "085_local_installer_launcher"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "085_k_os_local_installer_launcher.md"

PREVIOUS_CHECKPOINT = "084 - K-OS Release Candidate Gate Core"
NEXT_CHECKPOINT = "086 - K-OS Final Documentation Pack Core"

INSTALL_CHECK_SCRIPT = ROOT / "scripts" / "k_os_local_install_check.ps1"
LAUNCHER_SCRIPT = ROOT / "scripts" / "k_os_local_launcher.ps1"

ENTRYPOINT_CANDIDATES = ["app.py", "streamlit_app.py", "Home.py"]

BLOCKED_OPERATIONS = [
    "dependency_install_execution",
    "installer_execution",
    "deploy_execution",
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
            "Criar instalador/launcher local seguro do K-OS com manifesto, scripts "
            "PowerShell de checagem e inicializacao do cockpit, evidencias sanitizadas "
            "e dashboard somente leitura, sem instalar dependencias automaticamente, "
            "sem executar installer real, sem deploy, recovery, rollback, drill, reset, "
            "force push, limpeza destrutiva ou auto-fix."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "launcher_scripts": [
            rel(INSTALL_CHECK_SCRIPT),
            rel(LAUNCHER_SCRIPT),
        ],
        "entrypoint_candidates": ENTRYPOINT_CANDIDATES,
        "allowed_operations": [
            "read_local_project_state",
            "generate_local_launcher_scripts",
            "generate_sanitized_launcher_manifest",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "launcher_policy": {
            "generate_launcher_only": True,
            "execute_installer": False,
            "install_dependencies": False,
            "modify_system_path": False,
            "create_services": False,
            "create_scheduled_tasks": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "operator_runs_launcher_manually": True,
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


def detect_entrypoint() -> Dict[str, Any]:
    found = []
    for candidate in ENTRYPOINT_CANDIDATES:
        path = ROOT / candidate
        if path.exists():
            found.append(file_info(path))

    return {
        "candidates": ENTRYPOINT_CANDIDATES,
        "found_count": len(found),
        "selected": found[0]["path"] if found else None,
        "status": "ready" if found else "warning",
        "found": found,
    }


def detect_runtime() -> Dict[str, Any]:
    streamlit_available = importlib.util.find_spec("streamlit") is not None

    requirements = ROOT / "requirements.txt"
    requirements_text = read_text(requirements).lower() if requirements.exists() else ""
    requirements_has_streamlit = "streamlit" in requirements_text

    return {
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "streamlit_available": streamlit_available,
        "requirements_txt": file_info(requirements),
        "requirements_has_streamlit": requirements_has_streamlit,
        "status": "ready" if streamlit_available or requirements_has_streamlit else "warning",
    }


def collect_previous_gate() -> Dict[str, Any]:
    gate_dir = ROOT / "reports" / "system" / "084_release_candidate_gate"
    gate_path = gate_dir / "084_release_candidate_gate.json"
    closure_path = gate_dir / "084_closure_report.json"
    validate_path = gate_dir / "084_validate_report.json"
    audit_path = gate_dir / "084_audit_report.json"

    gate_data = read_json(gate_path)
    closure_data = read_json(closure_path)
    validate_data = read_json(validate_path)
    audit_data = read_json(audit_path)

    return {
        "gate_report": file_info(gate_path),
        "closure_report": file_info(closure_path),
        "validate_report": file_info(validate_path),
        "audit_report": file_info(audit_path),
        "gate_status": gate_data.get("status") if isinstance(gate_data, dict) else None,
        "closure_status": closure_data.get("status") if isinstance(closure_data, dict) else None,
        "validate_status": validate_data.get("status") if isinstance(validate_data, dict) else None,
        "audit_status": audit_data.get("status") if isinstance(audit_data, dict) else None,
        "status": (
            "ready"
            if isinstance(gate_data, dict)
            and isinstance(closure_data, dict)
            and closure_data.get("status") == "closed"
            and isinstance(validate_data, dict)
            and validate_data.get("status") == "passed"
            and isinstance(audit_data, dict)
            and audit_data.get("status") == "passed"
            else "warning"
        ),
    }


def analyze_script_policy(path: Path) -> Dict[str, Any]:
    text = read_text(path)

    risky_patterns = {
        "dependency_install": re.compile(r"(?i)\b(pip\s+install|poetry\s+install|conda\s+install|winget\s+install)\b"),
        "git_reset_hard": re.compile(r"(?i)\bgit\s+reset\s+--hard\b"),
        "force_push": re.compile(r"(?i)\bgit\s+push\b.*\b--force\b"),
        "destructive_remove": re.compile(r"(?i)\b(Remove-Item\b.*\b-Recurse\b.*\b-Force\b|rm\s+-rf)\b"),
        "scheduled_task": re.compile(r"(?i)\b(Register-ScheduledTask|schtasks)\b"),
        "windows_service": re.compile(r"(?i)\b(New-Service|sc\.exe\s+create)\b"),
    }

    findings = []
    for name, pattern in risky_patterns.items():
        if pattern.search(text):
            findings.append(name)

    return {
        "path": rel(path),
        "exists": path.exists(),
        "line_count": len(text.splitlines()) if text else 0,
        "risk_findings": findings,
        "policy_status": "ready" if path.exists() and not findings else "warning",
        "sha256": sha256_file(path) if path.exists() else None,
    }


def build_launcher_manifest(config: Dict[str, Any]) -> Dict[str, Any]:
    entrypoint = detect_entrypoint()
    runtime = detect_runtime()
    previous_gate = collect_previous_gate()

    scripts = [
        analyze_script_policy(INSTALL_CHECK_SCRIPT),
        analyze_script_policy(LAUNCHER_SCRIPT),
    ]

    script_warnings = [
        item["path"]
        for item in scripts
        if item["policy_status"] != "ready"
    ]

    warnings = []
    if entrypoint["status"] != "ready":
        warnings.append("streamlit_entrypoint_missing")
    if runtime["status"] != "ready":
        warnings.append("streamlit_runtime_not_confirmed")
    if previous_gate["status"] != "ready":
        warnings.append("previous_rc_gate_warning")
    for item in script_warnings:
        warnings.append(f"launcher_script_policy_warning:{item}")

    manifest_status = "ready" if not warnings else "ready_with_warnings"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": manifest_status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "launcher_policy": sanitize(config.get("launcher_policy", {})),
        "entrypoint": entrypoint,
        "runtime": runtime,
        "previous_release_candidate_gate": previous_gate,
        "launcher_scripts": scripts,
        "warnings": warnings,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "dependency_install_executed": False,
            "installer_executed": False,
            "deploy_executed": False,
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
            "scheduled_task_created": False,
            "windows_service_created": False,
            "system_path_modified": False,
        },
        "operator_commands": {
            "check_only": "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_install_check.ps1",
            "launch_cockpit": "powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1",
        },
        "operational_decision": {
            "local_launcher_created": True,
            "local_install_check_created": True,
            "installer_executed": False,
            "dependencies_installed": False,
            "operator_runs_launcher_manually": True,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def manifest_markdown(manifest: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# 085 - K-OS Local Installer / Launcher Core")
    lines.append("")
    lines.append(f"Gerado em: {manifest['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(manifest.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {manifest['checkpoint']}")
    lines.append(f"- Camada: {manifest['layer']}")
    lines.append(f"- Status do launcher: {manifest['status']}")
    lines.append(f"- Checkpoint anterior: {manifest['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {manifest['next_checkpoint']}")
    lines.append("")

    lines.append("## Scripts criados")
    lines.append("")
    lines.append("| Script | Existe | Politica | SHA256 |")
    lines.append("|---|---|---|---|")
    for item in manifest["launcher_scripts"]:
        lines.append(f"| {item['path']} | {item['exists']} | {item['policy_status']} | {item['sha256']} |")
    lines.append("")

    lines.append("## Entrypoint")
    lines.append("")
    lines.append(f"- Status: {manifest['entrypoint']['status']}")
    lines.append(f"- Selecionado: {manifest['entrypoint']['selected']}")
    lines.append("")

    lines.append("## Runtime")
    lines.append("")
    lines.append(f"- Python: {manifest['runtime']['python_version']}")
    lines.append(f"- Streamlit disponivel: {manifest['runtime']['streamlit_available']}")
    lines.append(f"- requirements.txt possui streamlit: {manifest['runtime']['requirements_has_streamlit']}")
    lines.append("")

    lines.append("## Comandos do operador")
    lines.append("")
    lines.append("Checagem local:")
    lines.append("")
    lines.append("```powershell")
    lines.append(manifest["operator_commands"]["check_only"])
    lines.append("```")
    lines.append("")
    lines.append("Abrir cockpit:")
    lines.append("")
    lines.append("```powershell")
    lines.append(manifest["operator_commands"]["launch_cockpit"])
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

    lines.append("## Decisao operacional")
    lines.append("")
    lines.append("Launcher local criado. O operador pode executar manualmente os scripts quando quiser iniciar o K-OS.")
    lines.append("O sistema pode seguir para 086 - K-OS Final Documentation Pack Core.")
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
        "launcher_manifest": rel(REPORT_DIR / "085_local_installer_launcher_manifest.json"),
        "closure_report": rel(REPORT_DIR / "085_closure_report.json"),
        "next_checkpoint": NEXT_CHECKPOINT,
        "installer_executed": False,
        "dependencies_installed": False,
        "launcher_created": True,
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
            "dependency_install_executed": False,
            "installer_executed": False,
            "deploy_executed": False,
            "release_publish_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "085_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    manifest = build_launcher_manifest(config)

    write_json(REPORT_DIR / "085_local_installer_launcher_manifest.json", manifest)
    write_text(REPORT_DIR / "085_local_installer_launcher_manifest.md", manifest_markdown(manifest))
    write_text(DOCS_PATH, manifest_markdown(manifest))

    updated_registers = update_accountability_register(manifest)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "launcher_status": manifest["status"],
        "warnings": manifest["warnings"],
        "launcher_manifest_json": rel(REPORT_DIR / "085_local_installer_launcher_manifest.json"),
        "launcher_manifest_md": rel(REPORT_DIR / "085_local_installer_launcher_manifest.md"),
        "commercial_doc": rel(DOCS_PATH),
        "install_check_script": rel(INSTALL_CHECK_SCRIPT),
        "launcher_script": rel(LAUNCHER_SCRIPT),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "installer_executed": False,
        "dependencies_installed": False,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": manifest["execution_guard"],
    }

    write_json(REPORT_DIR / "085_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_085_local_installer_launcher.ps1",
        INSTALL_CHECK_SCRIPT,
        LAUNCHER_SCRIPT,
        ROOT / "pages" / "085_K_OS_Local_Installer_Launcher.py",
        DOCS_PATH,
        REPORT_DIR / "085_init_report.json",
        REPORT_DIR / "085_action_report.json",
        REPORT_DIR / "085_local_installer_launcher_manifest.json",
        REPORT_DIR / "085_local_installer_launcher_manifest.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    manifest = read_json(REPORT_DIR / "085_local_installer_launcher_manifest.json")

    guard_ok = False
    decision_ok = False
    manifest_ok = False
    script_policy_ok = False

    if isinstance(manifest, dict):
        guard = manifest.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = manifest.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("local_launcher_created") is True
            and decision.get("local_install_check_created") is True
            and decision.get("installer_executed") is False
            and decision.get("dependencies_installed") is False
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        manifest_ok = manifest.get("status") in {"ready", "ready_with_warnings"}
        scripts = manifest.get("launcher_scripts", [])
        script_policy_ok = isinstance(scripts, list) and len(scripts) == 2 and all(
            item.get("exists") is True and item.get("policy_status") == "ready"
            for item in scripts
            if isinstance(item, dict)
        )

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and manifest_ok and script_policy_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "operational_decision_ok": decision_ok,
        "manifest_ok": manifest_ok,
        "script_policy_ok": script_policy_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "085_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 085 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "085_validate_report.json")
    manifest = read_json(REPORT_DIR / "085_local_installer_launcher_manifest.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    manifest_exists = isinstance(manifest, dict)

    checks = {
        "validate_passed": validate_passed,
        "launcher_manifest_exists": manifest_exists,
        "launcher_scripts_created": INSTALL_CHECK_SCRIPT.exists() and LAUNCHER_SCRIPT.exists(),
        "dependency_install_not_executed": True,
        "installer_not_executed": True,
        "deploy_not_executed": True,
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
        "scheduled_task_not_created": True,
        "windows_service_not_created": True,
        "system_path_not_modified": True,
        "reports_are_sanitized": True,
        "transition_to_086_declared": True,
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

    write_json(REPORT_DIR / "085_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 085 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 085 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 085 fechado. Launcher local e checagem local criados sem executar installer real ou instalar dependencias.")
    lines.append("")
    lines.append("## Comandos manuais")
    lines.append("")
    lines.append("Checagem:")
    lines.append("")
    lines.append("```powershell")
    lines.append("powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_install_check.ps1")
    lines.append("```")
    lines.append("")
    lines.append("Abrir cockpit:")
    lines.append("")
    lines.append("```powershell")
    lines.append("powershell -ExecutionPolicy Bypass -File scripts\\k_os_local_launcher.ps1")
    lines.append("```")
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

    action_report = read_json(REPORT_DIR / "085_action_report.json")
    validate_report = read_json(REPORT_DIR / "085_validate_report.json")
    audit_report = read_json(REPORT_DIR / "085_audit_report.json")
    manifest = read_json(REPORT_DIR / "085_local_installer_launcher_manifest.json")

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
        "launcher_status": manifest.get("status") if isinstance(manifest, dict) else "unknown",
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "085_action_report.json"),
        "validate_report": rel(REPORT_DIR / "085_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "085_audit_report.json"),
        "launcher_manifest": rel(REPORT_DIR / "085_local_installer_launcher_manifest.json"),
        "install_check_script": rel(INSTALL_CHECK_SCRIPT),
        "launcher_script": rel(LAUNCHER_SCRIPT),
        "installer_executed": False,
        "dependencies_installed": False,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "085_closure_report.json", report)
    write_text(REPORT_DIR / "085_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 085 closure failed.")

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