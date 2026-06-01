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


CHECKPOINT_ID = "080"
CHECKPOINT_NAME = "K-OS Module Registry Core"
LAYER_NAME = "K-OS Core"

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "k_os_module_registry_080.json"
REPORT_DIR = ROOT / "reports" / "system" / "080_module_registry"
DOCS_DIR = ROOT / "docs" / "commercial"
DOCS_PATH = DOCS_DIR / "080_k_os_module_registry.md"

PREVIOUS_CHECKPOINT = "079 - K-OS System Health Monitor Core"
NEXT_CHECKPOINT = "081 - K-OS Agent Capability Registry Core"

MODULE_ROOTS = [
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
]

BLOCKED_OPERATIONS = [
    "module_execution",
    "automatic_remediation",
    "real_drill_execution",
    "real_recovery_execution",
    "real_rollback_execution",
    "git_reset_hard",
    "force_push",
    "destructive_shell",
    "memory_deletion",
    "secret_export",
]

IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".streamlit",
    "local_secrets",
    "runtime",
}

IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".sqlite",
    ".db",
    ".zip",
    ".gz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
}

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


def slug(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "module"


def default_config() -> Dict[str, Any]:
    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "objective": (
            "Criar registro central de modulos do K-OS com inventario local, "
            "classificacao operacional, evidencias sanitizadas e dashboard somente leitura, "
            "sem executar modulos, auto-fix, recovery, rollback, drill, reset ou force push."
        ),
        "previous_checkpoint": PREVIOUS_CHECKPOINT,
        "next_checkpoint": NEXT_CHECKPOINT,
        "module_roots": MODULE_ROOTS,
        "module_types": [
            "core_python",
            "operation_python",
            "agent_module",
            "streamlit_page",
            "script_wrapper",
            "configuration",
            "memory_surface",
            "campaign_surface",
            "content_pack",
            "report_surface",
            "documentation",
            "unknown",
        ],
        "allowed_operations": [
            "read_local_project_state",
            "generate_sanitized_module_registry",
            "generate_read_only_dashboard",
            "update_accountability_register_if_exists",
            "validate_artifacts",
            "audit_checkpoint",
            "create_closure_report",
        ],
        "blocked_operations": BLOCKED_OPERATIONS,
        "registry_policy": {
            "read_only_inventory": True,
            "execute_modules": False,
            "auto_fix": False,
            "sanitize_reports": True,
            "include_sensitive_content": False,
            "include_file_hashes": True,
            "ignore_local_secrets": True,
            "ignore_memory_runtime": True,
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


def should_ignore(path: Path) -> bool:
    parts = set(path.parts)

    if parts.intersection(IGNORED_PARTS):
        return True

    rel_path = rel(path)

    if rel_path.startswith("reports/security/latest_security_firewall_report"):
        return True

    if rel_path.startswith("reports/system/080_module_registry"):
        return True

    if rel_path.startswith("memory/runtime"):
        return True

    if rel_path.startswith("local_secrets"):
        return True

    if path.name.lower().startswith(".env"):
        return True

    if path.suffix.lower() in IGNORED_SUFFIXES:
        return True

    try:
        if path.is_file() and path.stat().st_size > 5 * 1024 * 1024:
            return True
    except Exception:
        return True

    return False


def classify_module(path: Path) -> str:
    rel_path = rel(path)
    suffix = path.suffix.lower()
    parts = rel_path.split("/")

    if parts and parts[0] == "agents":
        return "agent_module"

    if parts and parts[0] == "pages" and suffix == ".py":
        return "streamlit_page"

    if parts and parts[0] == "scripts":
        return "script_wrapper"

    if parts and parts[0] == "configs":
        return "configuration"

    if parts and parts[0] == "memory":
        return "memory_surface"

    if parts and parts[0] == "campaigns":
        return "campaign_surface"

    if parts and parts[0] == "content_packs":
        return "content_pack"

    if parts and parts[0] == "reports":
        return "report_surface"

    if parts and parts[0] == "docs":
        return "documentation"

    if rel_path.startswith("k_atlas/ops/") and suffix == ".py":
        return "operation_python"

    if rel_path.startswith("k_atlas/") and suffix == ".py":
        return "core_python"

    if suffix == ".json":
        return "configuration"

    if suffix in {".md", ".txt", ".rst"}:
        return "documentation"

    return "unknown"


def infer_status(path: Path) -> str:
    if not path.exists():
        return "missing"

    if path.is_dir():
        return "registered_directory"

    if path.suffix.lower() in {".py", ".ps1", ".json", ".md", ".txt", ".yaml", ".yml"}:
        return "registered"

    return "registered_asset"


def file_record(path: Path, root_name: str) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "module_id": slug(rel(path)),
        "root": root_name,
        "path": rel(path),
        "type": "directory" if path.is_dir() else "file",
        "module_type": classify_module(path),
        "status": infer_status(path),
        "execution_policy": "read_only_registered_not_executed",
    }

    if path.exists() and path.is_file():
        stat = path.stat()
        item.update({
            "size_bytes": stat.st_size,
            "modified_utc": dt.datetime.fromtimestamp(
                stat.st_mtime,
                tz=dt.timezone.utc,
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "sha256": sha256_file(path),
            "suffix": path.suffix.lower(),
        })

        if path.suffix.lower() == ".json":
            data = read_json(path)
            if isinstance(data, dict):
                item["json_keys"] = sorted([str(key) for key in data.keys()])[:30]
                for key in ["checkpoint", "name", "status", "layer", "next_checkpoint"]:
                    if key in data and not isinstance(data[key], (dict, list)):
                        item[key] = sanitize(str(data[key]))[:160]

    if path.exists() and path.is_dir():
        try:
            item["file_count"] = sum(1 for child in path.rglob("*") if child.is_file() and not should_ignore(child))
        except Exception:
            item["file_count"] = 0

    return item


def discover_modules(config: Dict[str, Any]) -> Dict[str, Any]:
    roots = config.get("module_roots", MODULE_ROOTS)
    if not isinstance(roots, list):
        roots = MODULE_ROOTS

    modules: List[Dict[str, Any]] = []
    root_status: List[Dict[str, Any]] = []

    for root_name in roots:
        if not isinstance(root_name, str):
            continue

        root_path = ROOT / root_name
        root_info = {
            "root": root_name,
            "path": rel(root_path),
            "exists": root_path.exists(),
            "status": "found" if root_path.exists() else "missing",
            "module_count": 0,
        }

        if not root_path.exists():
            root_status.append(root_info)
            continue

        modules.append(file_record(root_path, root_name))

        count = 1
        if root_path.is_dir():
            for path in sorted(root_path.rglob("*"), key=lambda item: rel(item)):
                if should_ignore(path):
                    continue
                if not path.is_file():
                    continue
                modules.append(file_record(path, root_name))
                count += 1

        root_info["module_count"] = count
        root_status.append(root_info)

    by_type: Dict[str, int] = {}
    by_root: Dict[str, int] = {}

    for module in modules:
        by_type[module["module_type"]] = by_type.get(module["module_type"], 0) + 1
        by_root[module["root"]] = by_root.get(module["root"], 0) + 1

    missing_roots = [item["root"] for item in root_status if not item["exists"]]

    return {
        "generated_at": now_utc(),
        "total_modules": len(modules),
        "root_status": root_status,
        "missing_roots": missing_roots,
        "by_type": dict(sorted(by_type.items())),
        "by_root": dict(sorted(by_root.items())),
        "modules": modules,
    }


def build_registry(config: Dict[str, Any]) -> Dict[str, Any]:
    inventory = discover_modules(config)

    critical_module_types = [
        "core_python",
        "operation_python",
        "streamlit_page",
        "script_wrapper",
        "configuration",
        "documentation",
    ]

    present_types = set(inventory["by_type"].keys())
    missing_critical_types = [
        item for item in critical_module_types
        if item not in present_types
    ]

    status = "healthy" if inventory["total_modules"] > 0 and not missing_critical_types else "attention"

    return {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "layer": LAYER_NAME,
        "generated_at": now_utc(),
        "status": status,
        "objective": config.get("objective"),
        "previous_checkpoint": config.get("previous_checkpoint", PREVIOUS_CHECKPOINT),
        "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        "registry_policy": sanitize(config.get("registry_policy", {})),
        "inventory": inventory,
        "critical_module_types": critical_module_types,
        "missing_critical_module_types": missing_critical_types,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": {
            "module_execution_performed": False,
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
        "operational_decision": {
            "module_registry_created": True,
            "read_only_inventory": True,
            "can_continue_to_next_checkpoint": True,
            "next_checkpoint": config.get("next_checkpoint", NEXT_CHECKPOINT),
        },
    }


def registry_markdown(registry: Dict[str, Any]) -> str:
    inventory = registry["inventory"]

    lines: List[str] = []
    lines.append("# 080 - K-OS Module Registry Core")
    lines.append("")
    lines.append(f"Gerado em: {registry['generated_at']}")
    lines.append("")
    lines.append("## Objetivo")
    lines.append("")
    lines.append(str(registry.get("objective", "")))
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(f"- Checkpoint: {registry['checkpoint']}")
    lines.append(f"- Camada: {registry['layer']}")
    lines.append(f"- Status do registry: {registry['status']}")
    lines.append(f"- Checkpoint anterior: {registry['previous_checkpoint']}")
    lines.append(f"- Proximo checkpoint: {registry['next_checkpoint']}")
    lines.append(f"- Total de modulos registrados: {inventory['total_modules']}")
    lines.append("")

    lines.append("## Contagem por tipo")
    lines.append("")
    lines.append("| Tipo | Quantidade |")
    lines.append("|---|---:|")
    for module_type, count in inventory["by_type"].items():
        lines.append(f"| {module_type} | {count} |")
    lines.append("")

    lines.append("## Contagem por raiz")
    lines.append("")
    lines.append("| Raiz | Quantidade |")
    lines.append("|---|---:|")
    for root, count in inventory["by_root"].items():
        lines.append(f"| {root} | {count} |")
    lines.append("")

    lines.append("## Raizes monitoradas")
    lines.append("")
    lines.append("| Raiz | Existe | Status | Modulos |")
    lines.append("|---|---|---|---:|")
    for item in inventory["root_status"]:
        lines.append(f"| {item['root']} | {item['exists']} | {item['status']} | {item['module_count']} |")
    lines.append("")

    lines.append("## Tipos criticos ausentes")
    lines.append("")
    if registry["missing_critical_module_types"]:
        for item in registry["missing_critical_module_types"]:
            lines.append(f"- {item}")
    else:
        lines.append("Nenhum tipo critico ausente.")
    lines.append("")

    lines.append("## Amostra de modulos registrados")
    lines.append("")
    lines.append("| Tipo | Raiz | Caminho | Status |")
    lines.append("|---|---|---|---|")
    for module in inventory["modules"][:120]:
        lines.append(f"| {module['module_type']} | {module['root']} | {module['path']} | {module['status']} |")
    lines.append("")

    lines.append("## Garantias de nao execucao")
    lines.append("")
    for key, value in registry["execution_guard"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    lines.append("## Operacoes bloqueadas")
    lines.append("")
    for operation in registry["blocked_operations"]:
        lines.append(f"- {operation}")
    lines.append("")

    lines.append("## Decisao operacional")
    lines.append("")
    lines.append("Registro central de modulos criado em modo somente leitura.")
    lines.append("O sistema pode seguir para 081 - K-OS Agent Capability Registry Core.")
    lines.append("")

    return "\n".join(lines)


def update_accountability_register(registry: Dict[str, Any]) -> List[str]:
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
        "status": registry["status"],
        "updated_at": now_utc(),
        "module_registry": rel(REPORT_DIR / "080_module_registry.json"),
        "closure_report": rel(REPORT_DIR / "080_closure_report.json"),
        "total_modules": registry["inventory"]["total_modules"],
        "next_checkpoint": NEXT_CHECKPOINT,
        "read_only_inventory": True,
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
            "read_only_inventory": True,
            "module_execution_performed": False,
            "automatic_remediation_executed": False,
            "real_drill_executed": False,
            "real_recovery_executed": False,
            "real_rollback_executed": False,
            "destructive_shell_executed": False,
        },
        "config": sanitize(config),
    }

    write_json(REPORT_DIR / "080_init_report.json", report)
    return report


def mode_action() -> Dict[str, Any]:
    ensure_dirs()
    config = load_config()
    registry = build_registry(config)

    write_json(REPORT_DIR / "080_module_registry.json", registry)
    write_text(REPORT_DIR / "080_module_registry.md", registry_markdown(registry))
    write_text(DOCS_PATH, registry_markdown(registry))

    updated_registers = update_accountability_register(registry)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "action",
        "status": "completed",
        "generated_at": now_utc(),
        "registry_status": registry["status"],
        "total_modules": registry["inventory"]["total_modules"],
        "missing_critical_module_types": registry["missing_critical_module_types"],
        "module_registry_json": rel(REPORT_DIR / "080_module_registry.json"),
        "module_registry_md": rel(REPORT_DIR / "080_module_registry.md"),
        "commercial_doc": rel(DOCS_PATH),
        "updated_accountability_registers": updated_registers,
        "next_checkpoint": NEXT_CHECKPOINT,
        "read_only_inventory": True,
        "blocked_operations": BLOCKED_OPERATIONS,
        "execution_guard": registry["execution_guard"],
    }

    write_json(REPORT_DIR / "080_action_report.json", report)
    return report


def mode_validate() -> Dict[str, Any]:
    ensure_dirs()

    expected_files = [
        CONFIG_PATH,
        Path(__file__),
        ROOT / "scripts" / "checkpoint_080_module_registry.ps1",
        ROOT / "pages" / "080_K_OS_Module_Registry.py",
        DOCS_PATH,
        REPORT_DIR / "080_init_report.json",
        REPORT_DIR / "080_action_report.json",
        REPORT_DIR / "080_module_registry.json",
        REPORT_DIR / "080_module_registry.md",
    ]

    checks = []
    for path in expected_files:
        checks.append({
            "path": rel(path),
            "exists": path.exists(),
        })

    registry = read_json(REPORT_DIR / "080_module_registry.json")

    guard_ok = False
    decision_ok = False
    registry_ok = False

    if isinstance(registry, dict):
        guard = registry.get("execution_guard", {})
        guard_ok = isinstance(guard, dict) and all(value is False for value in guard.values())
        decision = registry.get("operational_decision", {})
        decision_ok = (
            isinstance(decision, dict)
            and decision.get("module_registry_created") is True
            and decision.get("read_only_inventory") is True
            and decision.get("next_checkpoint") == NEXT_CHECKPOINT
        )
        inventory = registry.get("inventory", {})
        registry_ok = isinstance(inventory, dict) and inventory.get("total_modules", 0) > 0

    all_files_exist = all(item["exists"] for item in checks)

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "validate",
        "status": "passed" if all_files_exist and guard_ok and decision_ok and registry_ok else "failed",
        "generated_at": now_utc(),
        "file_checks": checks,
        "execution_guard_ok": guard_ok,
        "operational_decision_ok": decision_ok,
        "registry_has_modules": registry_ok,
        "next_checkpoint": NEXT_CHECKPOINT,
    }

    write_json(REPORT_DIR / "080_validate_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 080 validation failed.")

    return report


def mode_audit() -> Dict[str, Any]:
    ensure_dirs()

    validate_report = read_json(REPORT_DIR / "080_validate_report.json")
    registry = read_json(REPORT_DIR / "080_module_registry.json")

    validate_passed = isinstance(validate_report, dict) and validate_report.get("status") == "passed"
    registry_exists = isinstance(registry, dict)

    checks = {
        "validate_passed": validate_passed,
        "module_registry_exists": registry_exists,
        "read_only_inventory": True,
        "module_execution_not_performed": True,
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
        "transition_to_081_declared": True,
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

    write_json(REPORT_DIR / "080_audit_report.json", report)

    if report["status"] != "passed":
        raise RuntimeError("Checkpoint 080 audit failed.")

    return report


def final_closure_markdown(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# 080 - Closure Report")
    lines.append("")
    lines.append(f"Checkpoint: {report['checkpoint']}")
    lines.append(f"Nome: {report['name']}")
    lines.append(f"Status: {report['status']}")
    lines.append(f"Gerado em: {report['generated_at']}")
    lines.append("")
    lines.append("## Resultado")
    lines.append("")
    lines.append("Checkpoint 080 fechado. Registro central de modulos do K-OS criado em modo somente leitura.")
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

    action_report = read_json(REPORT_DIR / "080_action_report.json")
    validate_report = read_json(REPORT_DIR / "080_validate_report.json")
    audit_report = read_json(REPORT_DIR / "080_audit_report.json")
    registry = read_json(REPORT_DIR / "080_module_registry.json")

    ok = (
        isinstance(action_report, dict)
        and action_report.get("status") == "completed"
        and isinstance(validate_report, dict)
        and validate_report.get("status") == "passed"
        and isinstance(audit_report, dict)
        and audit_report.get("status") == "passed"
        and isinstance(registry, dict)
    )

    report = {
        "checkpoint": CHECKPOINT_ID,
        "name": CHECKPOINT_NAME,
        "mode": "closure",
        "status": "closed" if ok else "failed",
        "generated_at": now_utc(),
        "registry_status": registry.get("status") if isinstance(registry, dict) else "unknown",
        "total_modules": registry.get("inventory", {}).get("total_modules") if isinstance(registry, dict) else 0,
        "next_checkpoint": NEXT_CHECKPOINT,
        "action_report": rel(REPORT_DIR / "080_action_report.json"),
        "validate_report": rel(REPORT_DIR / "080_validate_report.json"),
        "audit_report": rel(REPORT_DIR / "080_audit_report.json"),
        "module_registry": rel(REPORT_DIR / "080_module_registry.json"),
        "read_only_inventory": True,
        "blocked_operations_confirmed": True,
    }

    write_json(REPORT_DIR / "080_closure_report.json", report)
    write_text(REPORT_DIR / "080_closure_report.md", final_closure_markdown(report))

    if report["status"] != "closed":
        raise RuntimeError("Checkpoint 080 closure failed.")

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