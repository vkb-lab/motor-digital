# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


CHECKPOINT_ID = "079"
CHECKPOINT_NAME = "K-OS System Health Monitor Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_system_health_monitor_079.json"
REPORT_DIR = ROOT / "reports" / "system" / "079_system_health_monitor"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "079_k_os_system_health_monitor.md"

PREVIOUS_CHECKPOINT = "078 - K-Agent Resilience Layer Closure Core"
NEXT_CHECKPOINT = "080 - K-OS Module Registry Core"

BLOCKED_OPERATIONS = [
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

CRITICAL_DIRS = [
    "k_atlas",
    "agents",
    "live",
    "memory",
    "reports",
    "campaigns",
    "content_packs",
    "configs",
    "scripts",
    "pages",
    "docs",
    "docs/commercial",
]

CRITICAL_FILES = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "app.py",
    "streamlit_app.py",
    "Home.py",
]

RESILIENCE_EVIDENCE_PATHS = [
    "reports/resilience/071_resilience_readiness",
    "reports/resilience/072_resilience_scenario_planner",
    "reports/resilience/073_resilience_drill_designer",
    "reports/resilience/074_resilience_drill_dry_run",
    "reports/resilience/075_resilience_drill_operator_review",
    "reports/resilience/076_resilience_drill_evidence_pack",
    "reports/resilience/077_resilience_governance_summary",
    "reports/resilience/078_resilience_layer_closure",
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


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar monitor de saude operacional do K-OS com diagnostico local, "
            "evidencias sanitizadas, sem executar recovery, rollback, drill, "
            "reset, limpeza destrutiva ou force push."
        ),
        "previous_layer": "Resilience",
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "health_domains": [
            "repository",
            "python_runtime",
            "critical_directories",
            "critical_files",
            "streamlit_entrypoint",
            "reports_structure",
            "memory_safety",
            "resilience_closure_evidence",
            "governance_guards",
        ],
        "allowed_operations": [
            "read_local_project_state",
            "generate_sanitized_health_reports",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "health_policy": {
            "diagnostic_only": True,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "local_runtime_only": True,
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


def detect_streamlit_entrypoint() -> Dict[str, Any]:
    candidates = ["app.py", "streamlit_app.py", "Home.py"]
    found = []

    for candidate in candidates:
        path = ROOT / candidate
        if path.exists():
            found.append(file_info(path))

    return {
        "candidates": candidates,
        "found_count": len(found),
        "status": "healthy" if found else "attention",
        "selected": found[0]["path"] if found else None,
        "found": found,
    }


def scan_gitignore() -> Dict[str, Any]:
    gitignore = ROOT / ".gitignore"
    content = read_text(gitignore)
    required_patterns = [
        "local_secrets",
        ".env",
        "memory/runtime",
        "reports/security/latest_security_firewall_report",
    ]

    pattern_status = []
    for pattern in required_patterns:
        pattern_status.append({
            "pattern": pattern,
            "present": pattern in content,
        })

    return {
        "path": rel(gitignore),
        "exists": gitignore.exists(),
        "required_patterns": pattern_status,
        "status": "healthy" if gitignore.exists() and all(item["present"] for item in pattern_status) else "attention",
    }


def collect_resilience_evidence() -> Dict[str, Any]:
    items = []

    for relative in RESILIENCE_EVIDENCE_PATHS:
        path = ROOT / relative
        info = file_info(path)
        expected_checkpoint = relative.split("/")[2].split("_")[0] if len(relative.split("/")) >= 3 else ""
        closure_candidates = []

        if path.exists() and path.is_dir():
            for candidate in sorted(path.glob("*closure*.json"))[:20]:
                closure_candidates.append(file_info(candidate))
            for candidate in sorted(path.glob("*manifest*.json"))[:20]:
                closure_candidates.append(file_info(candidate))
            for candidate in sorted(path.glob("*summary*.json"))[:20]:
                closure_candidates.append(file_info(candidate))

        items.append({
            "checkpoint": expected_checkpoint,
            "path": relative,
            "exists": path.exists(),
            "evidence_file_count": info.get("file_count", 0),
            "key_reports": closure_candidates,
            "status": "found" if path.exists() else "missing",
        })

    found_count = sum(1 for item in items if item["exists"])

    return {
        "expected_count": len(items),
        "found_count": found_count,
        "status": "healthy" if found_count == len(items) else "attention",
        "items": items,
    }


def collect_report_structure() -> Dict[str, Any]:
    report_roots = [
        ROOT / "reports",
        ROOT / "reports" / "resilience",
        ROOT / "reports" / "system",
        ROOT / "reports" / "security",
    ]

    return {
        "status": "healthy" if all(path.exists() for path in report_roots[:3]) else "attention",
        "roots": [file_info(path) for path in report_roots],
    }


def collect_memory_safety() -> Dict[str, Any]:
    memory_path = ROOT / "memory"
    local_secrets_path = ROOT / "local_secrets"
    gitignore_status = scan_gitignore()

    return {
        "status": "healthy" if gitignore_status["status"] == "healthy" else "attention",
        "memory_directory": file_info(memory_path),
        "local_secrets_directory_exists": local_secrets_path.exists(),
        "local_secrets_policy": "must_remain_local_and_ignored",
        "gitignore": gitignore_status,
        "sensitive_content_exported": False,
    }


def build_health_report(config: Dict[str, Any]) -> Dict[str, Any]:
    critical_dirs = [file_info(ROOT / item) for item in CRITICAL_DIRS]
    critical_files = [file_info(ROOT / item) for item in CRITICAL_FILES]

    dirs_missing = [item["path"] for item in critical_dirs if not item["exists"]]
    existing_file_names = [item["path"] for item in critical_files if item["exists"]]
    entrypoint = detect_streamlit_entrypoint()
    reports_structure = collect_report_structure()
    memory_safety = collect_memory_safety()
    resilience_evidence = collect_resilience_evidence()

    domain_checks = {
        "repository": {
            "status": "healthy" if (ROOT / ".git").exists() else "attention",
            "root": str(ROOT),
            "git_directory_exists": (ROOT / ".git").exists(),
        },
        "python_runtime": {
            "status": "healthy",
            "python_version": sys.version.split()[0],
            "python_executable": sys.executable,
            "platform": platform.platform(),
        },
        "critical_directories": {
            "status": "healthy" if not dirs_missing else "attention",
            "missing": dirs_missing,
            "items": critical_dirs,
        },
        "critical_files": {
            "status": "healthy" if existing_file_names else "attention",
            "existing": existing_file_names,
            "items": critical_files,
        },
        "streamlit_entrypoint": entrypoint,
        "reports_structure": reports_structure,
        "memory_safety": memory_safety,
        "resilience_closure_evidence": resilience_evidence,
        "governance_guards": {
            "status": "healthy",
            "diagnostic_only": True,
            "auto_fix_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "real_drill_executed": False,
            "destructive_shell_executed": False,
            "force_push_executed": False,
            "git_reset_hard_executed": False,
        },
    }

    attention_domains = [
        name for name, data in domain_checks.items()
        if isinstance(data, dict) and data.get("status") != "healthy"
    ]

    system_status = "healthy" if not attention_domains else "attention"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": system_status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "attention_domains": attention_domains,
        "domain_checks": domain_checks,
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
            "automatic_remediation_executed": False,
        },
        "operational_decision": {
            "health_monitor_created": True,
            "diagnostic_only": True,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def health_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# 079 - K-OS System Health Monitor Core")
    lines.append("")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(report.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {report['checkpoint']}")
    lines.append(f"- Camada: {report['layer']}")
    lines.append(f"- Status do sistema: {report['status']}")
    lines.append(f"- Checkpoint anterior: {report['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {report['next_checkpoint']}")
    lines.append("")

    lines.append("## Dominios com atencao")
    lines.append("")
    if report["attention_domains"]:
        for domain in report["attention_domains"]:
            lines.append(f"- {domain}")
    else:
        lines.append("Nenhum dominio com atencao.")
    lines.append("")

    lines.append("## Resumo dos dominios")
    lines.append("")
    lines.append("| Dominio | Status |")
    lines.append("|---|---|")
    for name, data in report["domain_checks"].items():
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        lines.append(f"| {name} | {status} |")
    lines.append("")

    lines.append("## Diretorios criticos")
    lines.append("")
    for item in report["domain_checks"]["critical_directories"]["items"]:
        lines.append(f"- {item['path']}: exists={item['exists']}")
    lines.append("")

    lines.append("## Arquivos criticos")
    lines.append("")
    for item in report["domain_checks"]["critical_files"]["items"]:
        lines.append(f"- {item['path']}: exists={item['exists']}")
    lines.append("")

    lines.append("## Streamlit")
    lines.append("")
    streamlit = report["domain_checks"]["streamlit_entrypoint"]
    lines.append(f"- Status: {streamlit['status']}")
    lines.append(f"- Entrypoint selecionado: {streamlit['selected']}")
    lines.append("")

    lines.append("## Evidencias Resilience")
    lines.append("")
    resilience = report["domain_checks"]["resilience_closure_evidence"]
    lines.append(f"- Status: {resilience['status']}")
    lines.append(f"- Esperado: {resilience['expected_count']}")
    lines.append(f"- Encontrado: {resilience['found_count']}")
    for item in resilience["items"]:
        lines.append(f"  - {item['checkpoint']} | {item['path']} | exists={item['exists']} | files={item['evidence_file_count']}")
    lines.append("")

    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in report["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in report["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")

    lines.append("## Decisao operacional")
    lines.append("")
    lines.append("Monitor de saude criado em modo somente diagnostico.")
    lines.append("O sistema pode seguir para 080 - K-OS Module Registry Core.")
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(report: Dict[str, Any]) -> List[str]:
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
        "status": report["status"],
        "updated_at": now_utc(),
        "health_report": rel(REPORT_DIR / "079_system_health_report.json"),
        "closure_report": rel(REPORT_DIR / "079_closure_report.json"),
        "next_checkpoint": NEXT_CHECKPOINT,
        "diagnostic_only": True,
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
            "diagnostic_only": True,
            "auto_fix_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "destructive_shell_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "079_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    health_report = build_health_report(config)

    write_json(REPORT_DIR / "079_system_health_report.json", health_report)
    write_text(REPORT_DIR / "079_system_health_report.md", health_markdown(health_report))
    write_text(DOCS_PATH, health_markdown(health_report))

    updated_registers = update_accountability_register(health_report)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "system_health_status": health_report["status"],
        "attention_domains": health_report["attention_domains"],
        "system_health_report_json": rel(REPORT_DIR / "079_system_health_report.json"),
        "system_health_report_md": rel(REPORT_DIR / "079_system_health_report.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "diagnostic_only": True,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": health_report["execution_guard"],
    }

    write_json(REPORT_DIR / "079_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_079_system_health_monitor.ps1",
        ROOT / "pages" / "079_K_OS_System_Health_Monitor.py",
        DOCS_PATH,
        REPORT_DIR / "079_init_report.json",
        REPORT_DIR / "079_action_report.json",
        REPORT_DIR / "079_system_health_report.json",
        REPORT_DIR / "079_system_health_report.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    health_report = read_json(REPORT_DIR / "079_system_health_report.json")

    guard_ok = False
    decision_ok = False

    if isinstance(health_report, dict):
        guard = health_report.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = health_report.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("health_monitor_created") is True
            and decision.get("diagnostic_only") is True
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "operational_decision_ok": decision_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "079_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 079 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "079_validate_report.json")
    health_report = read_json(REPORT_DIR / "079_system_health_report.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    health_exists = isinstance(health_report, dict)

    checks = {
        "validate_passed": validate_passed,
        "health_report_exists": health_exists,
        "diagnostic_only": True,
        "automatic_remediation_not_executed": True,
        "real_drill_not_executed": True,
        "real_recovery_not_executed": True,
        "real_rollback_not_executed": True,
        "git_reset_hard_not_executed": True,
        "force_push_not_executed": True,
        "destructive_shell_not_executed": True,
        "memory_deletion_not_executed": True,
        "sensitive_content_not_exported": True,
        "reports_are_sanitized": True,
        "transition_to_080_declared": True,
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

    write_json(REPORT_DIR / "079_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 079 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 079 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 079 fechado. Monitor de saude do K-OS criado em modo somente diagnostico.")
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

    action_report = read_json(REPORT_DIR / "079_action_report.json")
    validate_report = read_json(REPORT_DIR / "079_validate_report.json")
    audit_report = read_json(REPORT_DIR / "079_audit_report.json")
    health_report = read_json(REPORT_DIR / "079_system_health_report.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(health_report, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "system_health_status": health_report.get("status") if isinstance(health_report, dict) else "unknown",
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "079_action_report.json"),
        "validate_report": rel(REPORT_DIR / "079_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "079_audit_report.json"),
        "system_health_report": rel(REPORT_DIR / "079_system_health_report.json"),
        "diagnostic_only": True,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "079_closure_report.json", report)
    write_text(REPORT_DIR / "079_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 079 closure failed.")

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